import queue
import mysocket
import socket
import json
import threading
from SmartLampServer import my_face_feature, my_pose_classify
from typing import Any
import my_img_process
import multiprocessing
import time


from global_const import FATIGUE_FLAG, POSE_FLAG


def function_call(msg, wd, sq) -> (int, Any):
    try:
        function = msg['function']
        argument = msg['argument']
    except KeyError as err:
        print('KeyError: ' + str(err))
        return_value = 'KeyError: ' + str(err) + '. Be sure to include [\'function\', \'argument\']'
        return -1, return_value
    if function == 'image_process':
        argument = my_img_process.base64_to_cv2(argument)

        wd.update_video(argument)

        is_eye_closed = -1
        pose = -1

        now_time = time.time_ns() // 100000000
        # print(now_time)

        if now_time % 35 == 3:
            eye_threading = threading.Thread(target=my_face_feature.is_eye_closed, args=(argument, sq, wd))
            eye_threading.start()
        else:
            # print('block 1 time')
            pass
        # is_eye_closed = my_face_feature.is_eye_closed(argument)

        if now_time % 40 == 1:
            pose_threading = threading.Thread(target=my_pose_classify.pose_classification, args=(argument, sq, wd))
            pose_threading.start()
        # pose = my_pose_classify.pose_classification(argument)

        # return 0, {'is_eye_close': is_eye_closed, 'pose_classify': pose}
    elif function == 'image_test':
        # img = my_img_process.base64_to_cv2(argument)
        # cv2.imshow('test_img', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        pass
        # return 0, 'Received.'
    else:
        pass
        # return 1, 'Unknown function name.'


def receive_tcp(rq: queue.Queue, client_socket: socket.socket):
    while True:
        try:
            datapack = mysocket.receive_tcp(client_socket)
        except Exception as msg:
            # print("unknown error: {0}".format(msg))
            break
        # print(len(datapack))
        rq.put((datapack, client_socket))


def receive_thread_tcp(rq: queue.Queue, server_socket):  #
    while True:
        client_socket, client_addr = server_socket.accept()
        # print('Connect with ' + client_addr[0] + ':' + str(client_addr[1]))
        thread = threading.Thread(target=receive_tcp, args=(rq, client_socket))
        # thread_list.append(thread)
        thread.start()


def decode_package(rq: queue.Queue, sq: queue.Queue, wd):  # rq:receive_queue  sq:send_queue
    while True:
        queue_message = rq.get()
        # queue_length = rq.qsize()
        # print("队列中包含的元素数量为:", queue_length)

        # print('decode_package(): get a message')
        message = json.loads(queue_message[0])
        # print(message)
        conn_socket = queue_message[1]
        conn_socket.close()
        # function_call(message, wd)
        p1 = threading.Thread(target=function_call, args=(message, wd, sq))
        p1.start()

        # status_code, return_value = function_call(message)
        """
        '''
        message
        {
            'function': 调用函数名
            'argument': 函数参数
        }
        '''
        reply = {
            'conn_socket': conn_socket.fileno(),
            'status_code': status_code,
            'reply': return_value
        }
        # print(" decode_package(): fileno = {0}".format(conn_socket.fileno()))
        # print(conn_socket)
        sq.put(json.dumps(reply))
        """


def reply_package(status_code, return_value, sq: queue.Queue):
    '''
            message
            {
                'function': 调用函数名
                'argument': 函数参数
            }
            '''
    reply = {
        'status_code': status_code,
        'reply': return_value
    }
    # print(" decode_package(): fileno = {0}".format(conn_socket.fileno()))
    # print(conn_socket)
    sq.put(json.dumps(reply))



def send_thread_tcp(sq: queue.Queue):
    while True:
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.loads(sq.get())
        # print("send_thread_tcp(): fileno = {0}".format(message['conn_socket']))
        # conn_socket = socket.socket(fileno=message['conn_socket'])
        # conn_socket = socket.fromfd(fd=message['conn_socket'], family=socket.AF_INET, type=socket.SOCK_STREAM)

        conn_socket = mysocket.connect_tcp(("192.168.1.102", 32334))

        # del message['conn_socket']
        # s.sendto(json.dumps(message).encode('utf-8'), tuple(send_address))
        # mysocket.send_udp(tuple(send_address), json.dumps(message).encode('utf-8'))
        mysocket.send_tcp(json.dumps(message).encode('utf-8'), conn_socket)
        # print('message send: ')
        # print(message)


def get_led_status():
    message = {'message_type': 'get_led_mode'}
    conn_socket = mysocket.connect_tcp(("192.168.1.102", 32334))
    mysocket.send_tcp(json.dumps(message).encode('utf-8'), conn_socket)
    reply = int(mysocket.receive_tcp(conn_socket))
    # print(f'current light status: {reply}')
    return reply

