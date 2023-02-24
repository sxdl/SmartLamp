import logging

import dlib
import numpy as np
import my_img_process
import cv2
import time
from configuration import MAX_EYE


# 将包含68个特征的的shape转换为numpy array格式
def feature2np(shape, d_type="int") -> np.ndarray:
    coord = np.zeros((68, 2), dtype=d_type)
    for i in range(0, 68):
        coord[i] = (shape.part(i).x, shape.part(i).y)
    return coord


# 将base64格式转成cv2格式；图片resize；转换为灰度图
def img_process(img):
    # img = my_img_process.base64_to_cv2(img)
    img = my_img_process.resize(img, width=500)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def face_feature(img) -> np.ndarray:
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    # processed_img = img_process(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    try:
        face = detector(img, 1)[0]  # 人脸位置检测，只取一张人脸
    except IndexError:
        return np.zeros((68, 2))
    shape = predictor(img, face)  # 人脸68特征点
    return feature2np(shape)


def distance(x, y):
    return np.sqrt(np.sum((x - y) ** 2))


def is_eye_closed(img) -> int:
    feature = face_feature(img)
    if not feature.sum():
        # img = my_img_process.base64_to_cv2(img)
        # cv2.putText(img, 'No Face', (10, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 200, 200), 1)
        # cv2.imwrite('./log/{0}.png'.format(time.time_ns()), img)
        return -1

    left_eye_height = (distance(feature[37], feature[41]) + distance(feature[38], feature[40]))/2
    right_eye_height = (distance(feature[43], feature[47]) + distance(feature[44], feature[46]))/2
    average_height = (left_eye_height + right_eye_height)/2
    left_eye_width = distance(feature[36], feature[49])
    right_eye_width = distance(feature[42], feature[45])
    average_width = (left_eye_width + right_eye_width)/2
    eye_height_width_ratio = average_height / average_width

    print(eye_height_width_ratio)
    logging.info(str(eye_height_width_ratio))

    # img = my_img_process.base64_to_cv2(img)
    '''debug only
    for (x, y) in feature:
        cv2.circle(img, (x, y), 1, (0, 0, 255), -1)
    '''
    if eye_height_width_ratio < (0.5 * MAX_EYE):
        '''debug only
        cv2.putText(img, 'Eye: Close', (10, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 200, 200), 1)
        cv2.imwrite('./log/{0}.png'.format(time.time_ns()), img)
        '''
        return 1
    else:
        '''debug only
        cv2.putText(img, 'Eye: Open', (10, 20), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 200, 200), 1)
        cv2.imwrite('./log/{0}.png'.format(time.time_ns()), img)
        '''
        return 0


def perclos() -> float:
    pass


def is_fatigue() -> bool:
    if perclos() >= 0.15:
        return True
    else:
        return False


if __name__ == "__main__":
    image = cv2.imread('test.png')
    print(is_eye_closed(image))
