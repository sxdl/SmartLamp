import mysocket
import socket
import queue
import threading
import sys
from mylogging import logging_fun
import myfunction
from qtwindow import VideoStreamWindow
from PyQt5.QtWidgets import QApplication


# 配置日志
logging_fun('server.log')

HOST = socket.gethostbyname(socket.gethostname())
PORT = 45000

server_socket = mysocket.create_tcp(HOST, PORT)

# os.system('python sunny.py --clientid=211152389324')  # 内网穿透服务


# 创建应用程序和主窗口
host = "0.0.0.0"  # 接收所有可用IP地址的数据包
port = 45001  # 实际使用的端口号
app = QApplication(sys.argv)
window = VideoStreamWindow(host, port)


# 创建消息队列
receive_queue = queue.Queue()
send_queue = queue.Queue()

# 接收进程
receive_thread = threading.Thread(target=myfunction.receive_thread_tcp, args=(receive_queue, server_socket))  # server_socket
receive_thread.start()


# 处理进程
process_thread = threading.Thread(target=myfunction.decode_package, args=(receive_queue, send_queue, window))
process_thread.start()


# 发送进程
send_thread = threading.Thread(target=myfunction.send_thread_tcp, args=(send_queue,))
send_thread.start()


window.show()
sys.exit(app.exec_())
