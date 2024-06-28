import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import socket
import json
import my_img_process
import mysocket


# 用于更新信息的接口
class InformationUpdater:
    def __init__(self):
        self.fatigue_level = 0.06
        self.pose = 'None'

    def update_information(self, fatigue_level=None, pose=None):
        poses = {0: 'book', 1: 'desktop', 2: 'mobile', 3: 'relax', 4: 'stand', -1: 'no person'}
        # print(f'fatigue: {fatigue_level}')
        if fatigue_level:
            self.fatigue_level += fatigue_level
            if self.fatigue_level <= 0:
                self.fatigue_level += 0.01
            if self.fatigue_level >= 0.14:
                self.fatigue_level -= 0.01
        if type(pose) == int:
            print(f'pose: {pose}')
            self.pose = poses[pose]

# 继承自QMainWindow的主窗口类
class VideoStreamWindow(QMainWindow):
    def __init__(self, host, port):
        self.q_img = None
        self.pixmap = None
        super().__init__()

        # 创建UDP套接字
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))

        # 初始化信息更新接口
        self.information_updater = InformationUpdater()

        # 创建视频展示区域和信息展示区域
        self.video_label = QLabel(self)
        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignCenter)

        # 创建主布局
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.info_label)

        # 创建主窗口
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # 设置定时器以更新视频流和信息
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_video)
        # self.timer.start(30)  # 更新间隔：30毫秒

    # 更新视频流和信息
    def update_video(self, frame):
        # self.socket.listen(10)
        # data = mysocket.receive_tcp(self.socket)
        # print(len(data))
        # # data, addr = self.socket.recvfrom(95535)  # 接收UDP数据
        # argument = json.loads(data)['argument']
        # frame = my_img_process.base64_to_cv2(argument)

        # frame = np.frombuffer(data, dtype=np.uint8)  # 将数据转换为帧图像的NumPy数组
        # frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)  # 解码图像数据

        # 在此处添加其他Python程序处理帧图像的代码
        # 例如，计算疲劳程度和情绪，并使用信息更新接口更新相关信息

        # 释放之前的QImage和QPixmap对象
        if self.q_img is not None:
            # print('clear q_img')
            self.q_img = None
        if self.pixmap is not None:
            # print('clear pixmap')
            self.pixmap = None

        # 将帧图像显示在窗口上
        if frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            self.q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.pixmap = QPixmap.fromImage(self.q_img)
            scaled_pixmap = self.pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio)
            self.video_label.setPixmap(scaled_pixmap)

        # # 更新信息展示区域
        info_text = f"Fatigue Level: {self.information_updater.fatigue_level:.2f}\nPose: {self.information_updater.pose}"
        self.info_label.setText(info_text)

        # 手动触发Qt事件处理，确保及时释放内存
        QApplication.processEvents()

    def update_information(self, is_eye_closed_result=None, pose_classification_result=None):
        # 在这里执行更新信息展示区域的操作
        self.information_updater.update_information(is_eye_closed_result, pose_classification_result)


# 主函数
if __name__ == "__main__":
    # 指定UDP视频流的IP地址和端口
    host = "0.0.0.0"  # 这里使用0.0.0.0表示接收所有可用IP地址的数据包
    port = 45001  # 请替换为实际使用的端口号

    # 创建应用程序和主窗口
    app = QApplication(sys.argv)
    window = VideoStreamWindow(host, port)
    window.show()
    sys.exit(app.exec_())
