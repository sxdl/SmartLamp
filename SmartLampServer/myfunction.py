import queue
import mysocket
import socket
import json
import threading
import my_face_feature
from SmartLampServer import my_pose_classify
from typing import Any
import my_img_process
import struct


def function_call(msg) -> (int, Any):
    try:
        function = msg['function']
        argument = msg['argument']
    except KeyError as err:
        print('KeyError: ' + str(err))
        return_value = 'KeyError: ' + str(err) + '. Be sure to include [\'function\', \'argument\']'
        return -1, return_value
    if function == 'image_process':
        argument = my_img_process.base64_to_cv2(argument)
        is_eye_closed = my_face_feature.is_eye_closed(argument)
        pose = my_pose_classify.pose_classification(argument)
        return 0, {'is_eye_close': is_eye_closed, 'pose_classify': pose}
    elif function == 'image_test':
        # img = my_img_process.base64_to_cv2(argument)
        # cv2.imshow('test_img', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return 0, 'Received.'
    else:
        return 1, 'Unknown function name.'


def receive_tcp(rq: queue.Queue, client_socket: socket.socket):
    while True:
        try:
            datapack = mysocket.receive_tcp(client_socket)
        except Exception as msg:
            # print("unknown error: {0}".format(msg))
            break
        # print(len(datapack))
        rq.put((datapack, client_socket))


def receive_thread_tcp(rq: queue.Queue, server_socket: socket.socket):
    while True:
        client_socket, client_addr = server_socket.accept()
        # print('Connect with ' + client_addr[0] + ':' + str(client_addr[1]))
        thread = threading.Thread(target=receive_tcp, args=(rq, client_socket))
        # thread_list.append(thread)
        thread.start()


def decode_package(rq: queue.Queue, sq: queue.Queue):  # rq:receive_queue  sq:send_queue
    while True:
        queue_message = rq.get()
        # print('decode_package(): get a message')
        message = json.loads(queue_message[0])
        # print(message)
        conn_socket = queue_message[1]
        status_code, return_value = function_call(message)
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


def send_thread_tcp(sq: queue.Queue):
    while True:
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = json.loads(sq.get())
        # print("send_thread_tcp(): fileno = {0}".format(message['conn_socket']))
        # conn_socket = socket.socket(fileno=message['conn_socket'])
        conn_socket = socket.fromfd(fd=message['conn_socket'], family=socket.AF_INET, type=socket.SOCK_STREAM)
        # print(conn_socket)
        del message['conn_socket']
        # s.sendto(json.dumps(message).encode('utf-8'), tuple(send_address))
        # mysocket.send_udp(tuple(send_address), json.dumps(message).encode('utf-8'))
        mysocket.send_tcp(json.dumps(message).encode('utf-8'), conn_socket)
        # print('message send: ')
        print(message)
