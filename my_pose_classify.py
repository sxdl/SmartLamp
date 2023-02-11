import tensorflow as tf
import numpy as np
from tensorflow import keras
import pandas as pd
import os
import sys

pose_sample_rpi_path = 'raspberry_pi'
sys.path.append(pose_sample_rpi_path)

import utils
from data import BodyPart
from ml import Movenet

'''
movenet标记关键点
'''
movenet = Movenet('movenet_thunder')


def detect(image_path):
    image = tf.io.read_file(image_path)
    image = tf.io.decode_jpeg(image)
    image_height, image_width, channel = image.shape

    person = movenet.detect(image.numpy(), reset_crop_region=False)

    # Get landmarks and scale it to the same size as the input image
    pose_landmarks = np.array(
        [[keypoint.coordinate.x, keypoint.coordinate.y, keypoint.score]
         for keypoint in person.keypoints],
        dtype=np.float32)

    # Write the landmark coordinates to its per-class CSV file
    coordinates = pose_landmarks.flatten().astype('float64')
    coordinates = np.reshape(coordinates, (1, 51))
    # csv_out_writer.writerow([image_name] + coordinates)

    return coordinates


def pose_classification(image_path):
    x_input = detect(image_path)

    '''
    导入姿势分类模型
    '''
    model = keras.models.load_model('sit_pose_model.h5', custom_objects={'relu6': keras.layers.ReLU(6.), 'DepthwiseConv2D': keras.layers.DepthwiseConv2D})

    y_predict = model.predict(x_input)
    y_predict = np.argmax(y_predict, axis=1)[0]
    '''
    book: 0
    desktop: 1
    mobile: 2
    '''
    return y_predict
