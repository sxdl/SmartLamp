import mysocket
import socket
import queue
import threading
import sys
from mylogging import logging_fun
import myfunction

# 配置日志
logging_fun('server.log')

HOST = socket.gethostbyname(socket.gethostname())
PORT = 45000

server_socket = mysocket.create_tcp(HOST, PORT)

# os.system('python sunny.py --clientid=211152389324')  # 内网穿透服务

# 创建消息队列
receive_queue = queue.Queue()
send_queue = queue.Queue()

# 接收进程
receive_thread = threading.Thread(target=myfunction.receive_thread_tcp, args=(receive_queue, server_socket))
receive_thread.start()


# 处理进程
process_thread = threading.Thread(target=myfunction.decode_package, args=(receive_queue, send_queue))
process_thread.start()


# 发送进程
send_thread = threading.Thread(target=myfunction.send_thread_tcp, args=(send_queue,))
send_thread.start()
