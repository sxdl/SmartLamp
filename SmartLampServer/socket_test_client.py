import base64
import socket
import threading
import sys
# import encodings
import json
import cv2
import my_img_process
import time
import mysocket


HOST = 'api.sxdl.site'  # 'vipgz4.91tunnel.com'
PORT = 10049

s = mysocket.connect_tcp((HOST, PORT))

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print("socket created.")
#
# try:
#     s.connect((HOST, PORT))
# except socket.error as msg:
#     print('Connect failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
#     sys.exit()
#
# print('socket connected to ' + HOST + ':' + str(PORT))

# message = 'helloworld'.encode('utf-8')
#
# s.sendall(message)
# print('message send: ' + str(message))

# message = {
#     'function': 123,
#     'argument': 'hello there!'
# }
# # json_message = json.dumps(message)
#
# s.sendto(json.dumps(message).encode('utf-8'), (HOST, PORT))
#
# print('message send: ' + str(message))


cv_image = cv2.imread('test.png')
# cv_image = cv2.imencode('.jpg', cv_image)
image = cv2.imencode('.jpg', cv_image)[1]
# img = str(base64.b64encode(image))
img = str(base64.b64encode(image))[2:-1]

message = {
    'function': 'image_process',
    'argument': img
}
# json_message = json.dumps(message)
print(len(img))
start = time.perf_counter()

mysocket.send_tcp(json.dumps(message).encode('utf-8'), s)
# s.send("hello".encode('utf-8'))

# s.sendto(json.dumps(message).encode('utf-8'), (HOST, PORT))

# print('message send: ' + str(message))

reply = mysocket.receive_tcp(s)
print(reply)
# s.close()
print(s)
time.sleep(0)
mysocket.send_tcp(json.dumps(message).encode('utf-8'), s)
reply = mysocket.receive_tcp(s)
end = time.perf_counter()

print(reply)
print('total time: {0}s.'.format(end-start))
