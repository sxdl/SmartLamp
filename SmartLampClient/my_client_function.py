import logging
import queue
import socket
from SmartLampServer.my_face_feature import img_process
from my_img_process import *
from my_light_control import set_led_mode
from configuration import *
import mysocket
import threading
import json
import os
import bluetooth
import time


def connect_internet() -> bool:
    ipaddress = socket.gethostbyname(socket.gethostname())
    if ipaddress == "127.0.0.1":
        print('Err: not connected to Internet!')
        return False
    else:
        return True


def send_and_reply(datapack: bytes, conn_socket: socket.socket, mq: queue.Queue):
    mysocket.send_tcp(datapack, conn_socket)
    message = mysocket.receive_tcp(conn_socket)
    mq.put(message)


def image_send_thread(conn_socket: socket.socket, cap, mq: queue.Queue):
    print("image_send_thread()")
    while True:
        img = cap.read()[1]  # 获取摄像头图片
        img = img_process(img)
        img = cv2_to_base64(img)
        message = {
            'function': 'image_process',
            'argument': img
        }
        s = mysocket.connect_tcp(SERVER_ADDR)
        send_thread = threading.Thread(target=send_and_reply, args=(json.dumps(message).encode('utf-8'), s, mq))
        send_thread.start()
        time.sleep(1.5)  # 20帧


def message_address_thread(rq: queue.Queue, fq: queue.Queue, pq: queue.Queue):
    """
    :param rq: reply_queue 服务器返回数据消息队列
    :param fq: fatigue_queue 疲劳检测模块消息队列
    :param pq: pose_queue 姿势分类模块消息队列
    :return: None
    """
    while True:
        '''
            message = {
                'status_code': [int],
                'reply': dict['is_eye_close': [int],
                              'pose_classify': [int],]
            }
            '''
        message = json.loads(rq.get())
        status_code = message['status_code']
        reply = message['reply']
        is_eye_close = reply['is_eye_close']
        pose_classify = reply['pose_classify']
        fatigue_message = {
            'reply': is_eye_close
        }
        fq.put(json.dumps(fatigue_message))
        pose_message = {
            'reply': pose_classify
        }
        pq.put(json.dumps(pose_message))
        # print(message)


def fatigue_detection_judge_thread(conn_socket: socket.socket, mq: queue.Queue, strip):  # strip
    print('fatigue_detection_judge_thread()')
    is_eye_closed_list = [0] * FATIGUE_DETECT_FREQUENCY
    perclos_sum = 0
    while True:
        '''
        message = {
            # 'status_code': status_code,
            'reply': Union[0,1,-1]
        }
        '''
        message = json.loads(mq.get())
        # print(message)
        # status_code = message['status_code']
        reply = message['reply']
        if reply < 0:  # 若非零，则返回值异常
            continue
        # 计算PERCLOS值,0.15为阈值
        perclos_sum += reply
        perclos_sum -= is_eye_closed_list[0]
        perclos = perclos_sum / FATIGUE_DETECT_FREQUENCY
        print('PERCLOS: {0}'.format(perclos))
        logging.info('PERCLOS: {0}'.format(perclos))

        is_eye_closed_list.append(reply)
        del is_eye_closed_list[0]

        if perclos > 0.15:
            print('疲劳')
            set_led_mode(strip, 1)


# def fatigue_detection_thread(conn_socket, cap, mq: queue.Queue, strip):
#


def ble_pair():
    # while True:
    #     print("performing inquiry...")
    #     nearby_devices = bluetooth.discover_devices(lookup_names=True)
    #     print("found %d devices" % len(nearby_devices))
    #     for addr, name in nearby_devices:
    #         print("  %s - %s" % (addr, name))
    #     time.sleep(5)

    os.system("bluetoothctl power on")
    os.system("bluetoothctl discoverable on")

    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)

    port = server_sock.getsockname()[1]

    uuid = "00001101-0000-1000-8000-00805F9B34FB"

    bluetooth.advertise_service(server_sock, "SampleServer", service_id=uuid,
                                service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                # protocols=[bluetooth.OBEX_UUID]
                                )

    print("Waiting for connection on RFCOMM channel", port)

    client_sock, client_info = server_sock.accept()
    print("Accepted connection from", client_info)
    client_sock.recv(10)
    return client_sock


def command_process(strip, blt_sock):
    print("command_process")
    while True:
        # try:
        #     ser = serial.Serial("/dev/rfcomm0", 9600)  # 开启串口，波特率为9600
        # except:
        #     time.sleep(5)
        #     continue

        '''
        head = packSize
        command = {
            func : FunctionName
            args : Arguments
        }
        '''
        size = int(blt_sock.recv(2).decode('utf-16'))  # 包大小
        command = json.loads(blt_sock.recv(size))
        function_name = command['func']
        args = command['args']

        if function_name == "set_led_mode":
            arg = int(args)
            set_led_mode(strip, arg)
        # ser.close()  # 关闭串口
