import mysocket
from my_client_function import *
from my_light_control import led_setup, set_led_mode
import threading
import cv2
import queue
from mylogging import logging_fun2


'''
set up
'''
# 配置日志
logging_fun2('client.log')

# 初始化灯带(strip)
if True:
    strip = led_setup()
    set_led_mode(strip, 3)

# 开启摄像头
cap = cv2.VideoCapture(0)
# 尝试连接蓝牙
if True:
    blt_sock = ble_pair()

# "sudo rfcomm watch hci0" 树莓派等待蓝牙连接
# 远程控制指令接收线程
if True:
    command_thread = threading.Thread(target=command_process, args=(strip, blt_sock))
    command_thread.start()

# 创建消息队列
reply_queue = queue.Queue()  # 服务器返回信息消息队列
fatigue_queue = queue.Queue()  # 疲劳检测模块消息队列
pose_queue = queue.Queue()  # 姿势分类消息队列

# 尝试连接Internet
if connect_internet():
    conn_socket = mysocket.connect_tcp(SERVER_ADDR)  # 连接远程服务器

    # # 疲劳检测模块
    # fatigue_detection_thread(conn_socket, cap, img_queue, strip)

    # 图像发送线程
    send_thread = threading.Thread(target=image_send_thread, args=(conn_socket, cap, reply_queue))
    send_thread.start()

    # 接收线程 分发数据到不同模块消息队列
    address_thread = threading.Thread(target=message_address_thread, args=(reply_queue, fatigue_queue, pose_queue))
    address_thread.start()

    # PERCLOS 计算线程 疲劳检测模块
    judge_thread = threading.Thread(target=fatigue_detection_judge_thread, args=(conn_socket, strip))  # strip
    judge_thread.start()

    # TODO 姿势分类模块


