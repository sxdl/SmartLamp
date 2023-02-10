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
strip = led_setup()
set_led_mode(strip, 3)

# 开启摄像头
cap = cv2.VideoCapture(0)
# 尝试连接蓝牙
ble_pair()

# "sudo rfcomm watch hci0" 树莓派等待蓝牙连接
# 远程控制指令接收线程
command_thread = threading.Thread(target=command_process, args=(strip,))
command_thread.start()

# 创建消息队列
img_queue = queue.Queue()

# 尝试连接Internet
if connect_internet() and False:
    # 疲劳检测模块
    fatigue_detection_thread(cap, img_queue, strip)


