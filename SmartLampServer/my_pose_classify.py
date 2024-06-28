import tensorflow as tf
import numpy as np
from tensorflow import keras
import pandas as pd
import os
import sys
import json
import queue
import myfunction
import time
import cv2

pose_sample_rpi_path = 'raspberry_pi'
sys.path.append(pose_sample_rpi_path)

import utils
from data import BodyPart
from ml import Movenet

'''
movenet标记关键点
'''
movenet = Movenet('lite-model_movenet_singlepose_lightning_tflite_int8_4')  # lite-model_movenet_singlepose_lightning_3
# movenet = Movenet('lite-model_movenet_singlepose_lightning_3')  # movenet_thunder


# Define function to run pose estimation using MoveNet Thunder.
# You'll apply MoveNet's cropping algorithm and run inference multiple times on
# the input image to improve pose estimation accuracy.
def ddetect(input_tensor, inference_count=3):
    """Runs detection on an input image.

    Args:
      input_tensor: A [height, width, 3] Tensor of type tf.float32.
        Note that height and width can be anything since the image will be
        immediately resized according to the needs of the model within this
        function.
      inference_count: Number of times the model should run repeatly on the
        same input image to improve detection accuracy.

    Returns:
      A Person entity detected by the MoveNet.SinglePose.
    """
    image_height, image_width, channel = input_tensor.shape

    # Detect pose using the full input image
    movenet.detect(input_tensor.numpy(), reset_crop_region=True)

    # Repeatedly using previous detection result to identify the region of
    # interest and only croping that region to improve detection accuracy
    for _ in range(inference_count - 1):
        person = movenet.detect(input_tensor.numpy(),
                                reset_crop_region=False)

    return person


def reply_package(message_type, status_code, return_value, sq: queue.Queue):
    '''
            message
            {
                'function': 调用函数名
                'argument': 函数参数
            }
            '''
    reply = {
        'message_type': message_type,
        'status_code': status_code,
        'reply': return_value
    }
    # print(" decode_package(): fileno = {0}".format(conn_socket.fileno()))
    # print(conn_socket)
    sq.put(json.dumps(reply))


def detect(img: np.ndarray):
    # image = tf.io.read_file(image_path)
    # img = tf.convert_to_tensor(img, dtype=np.str)
    # img = img.astype(np.int64)
    # image = tf.io.decode_jpeg(img)
    # image_height, image_width, channel = image.shape

    img = tf.convert_to_tensor(img)
    # img = tf.convert_to_tensor(np.flip(img, axis=-1))
    # image = tf.compat.v1.image.decode_jpeg(img)
    # image = tf.expand_dims(img, axis=0)
    # image = tf.image.resize_with_pad(image, 144, 192)
    #
    # # Initialize the TFLite interpreter
    # interpreter = tf.lite.Interpreter(model_path="lite-model_movenet_singlepose_lightning_3.tflite")
    # interpreter.allocate_tensors()
    #
    # # TF Lite format expects tensor type of float32.
    # input_image = tf.cast(image, dtype=tf.float32)
    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()
    #
    # interpreter.set_tensor(input_details[0]['index'], input_image.numpy())
    #
    # interpreter.invoke()
    #
    # # Output is a [1, 1, 17, 3] numpy array.
    # person = interpreter.get_tensor(output_details[0]['index'])
    # pose_landmarks = person.reshape((17, 3))

    image_height, image_width, channel = img.shape
    # print(f'height, width, channel: {image_height},{image_width}, {channel}')
    person = ddetect(img)  # , reset_crop_region=False

    # Get landmarks and scale it to the same size as the input image
    pose_landmarks = np.array(
        [[keypoint.coordinate.x, keypoint.coordinate.y, keypoint.score]
         for keypoint in person.keypoints],
        dtype=np.float32)

    # If every point score are less than 0.5, there is no person
    max_score = np.max(pose_landmarks[:, 2], axis=0)
    if max_score < 0.5:
        return 0

    # Write the landmark coordinates to its per-class CSV file
    coordinates = pose_landmarks.flatten().astype('float64')
    coordinates = np.reshape(coordinates, (1, 51))
    # csv_out_writer.writerow([image_name] + coordinates)

    return coordinates


NO_PERSON_FLAG = 0
STATUS_COLD_TICK = 0


def pose_classification(image, sq, wd) -> int:
    """Input an image and return pose classification. The image must be 3 channel.
    Returns
        book: 0.
        desktop: 1,
        mobile: 2,
        no person: -1
    """
    try:
        x_input = detect(image)
    except:
        return -1
    global NO_PERSON_FLAG, STATUS_COLD_TICK
    if type(x_input) == int:
        if myfunction.get_led_status() > 0:
            NO_PERSON_FLAG += 1
            if NO_PERSON_FLAG >= 3:
                reply_package('set_led_mode', 0, 0, sq)
                NO_PERSON_FLAG = 0
        print(f"'pose: is_eye_close': -1, 'pose_classify': -1")
        wd.update_information(pose_classification_result=-1)
        return -1

    '''
    导入姿势分类模型
    '''
    model = keras.models.load_model('sit_pose_model-0727.h5', custom_objects={'relu6': keras.layers.ReLU(6.), 'DepthwiseConv2D': keras.layers.DepthwiseConv2D})

    y_predict = model.predict(x_input)
    y_predict = np.argmax(y_predict, axis=1)[0]

    if y_predict != 4:  # myfunction.get_led_status() == 0 and
        if y_predict == 0:  # book
            STATUS_COLD_TICK = 4
            reply_package('set_led_mode', 0, 4, sq)
        elif y_predict == 1:  # desktop
            STATUS_COLD_TICK -= 1
            if STATUS_COLD_TICK <= 0:
                reply_package('set_led_mode', 0, 5, sq)
                STATUS_COLD_TICK = 0
        elif y_predict == 2:  # mobile
            STATUS_COLD_TICK = 4
            reply_package('set_led_mode', 0, 5, sq)
        elif y_predict == 3:  # relax
            STATUS_COLD_TICK = 4
            reply_package('set_led_mode', 0, 1, sq)

    # reply_package(0, {'is_eye_close': -1, 'pose_classify': int(y_predict)}, sq)
    # cv2.imwrite(f'pic/{time.time_ns()}.png', image)
    # print(f"'pose: is_eye_close': -1, 'pose_classify': {y_predict}")
    wd.update_information(pose_classification_result=int(y_predict))
    return int(y_predict)


# pose_classification('a88.png')
