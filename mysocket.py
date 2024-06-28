import socket
import sys
import struct
import time

buff_size = 1024


def send_tcp(datapack: bytes, conn_socket: socket.socket):
    data_len = len(datapack)
    conn_socket.send(struct.pack('Q', data_len))
    time.sleep(0.05)
    conn_socket.send(datapack)


def receive_tcp(conn_socket: socket.socket) -> str:
    # print("receive_tcp(): ")
    # print(conn_socket)
    header_size = 8
    while True:
        head_message = conn_socket.recv(header_size)  # header_size
        if len(head_message) != 8:
            # print('Error: except 8 bytes, received {0} bytes.'.format(len(head_message)))
            # print('Message: {0}'.format(head_message))
            continue
        elif len(head_message) == 8:
            break
    pack_size = struct.unpack('Q', head_message)[0]
    # print('等待接收包大小：{0}'.format(pack_size))
    data_buff = bytes()
    while True:
        data = conn_socket.recv(buff_size)
        data_buff += data
        # print('收到一个包，当前总共收到：{0}'.format(len(data_buff)))
        if len(data_buff) == pack_size:
            # print('收完啦')
            break
    # print(len(data_buff))
    return data_buff.decode('utf-8')


def send_udp(address, datapack, udp_socket: socket.socket):
    data_len = len(datapack)
    pack_num = 60
    if data_len % 60 != 0:
        buffer = data_len // pack_num + 1
    else:
        buffer = data_len // pack_num
    while True:
        send_data = datapack
        pack_number = 0
        while data_len >= buffer:
            udp_socket.sendto(struct.pack(f'i{buffer}s', pack_number, send_data[:buffer]), address)
            send_data = send_data[buffer:]
            data_len -= buffer
            pack_number += 1
        if 0 < data_len < buffer:
            udp_socket.sendto(struct.pack('i{0}s'.format(data_len), pack_number, send_data), address)
            break
        # udp_socket.sendto(b"end", address)
        reply = udp_socket.recvfrom(4)
        if reply[1] == address and reply[0] == "ok":
            break


def receive_udp(udp_socket: socket.socket):
    buffer = 1024
    received_data = {}  # 用于缓存接收到的数据包
    expected_pack_number = 0  # 下一个期望接收的包号
    address = None

    while True:
        try:
            data, addr = udp_socket.recvfrom(1500)  # 接收数据包和包号
            pack_number, pack_data = struct.unpack(f'i{len(data)-4}s', data)

            if address is None:
                address = addr  # 记录发送端地址，以便回复

            # 如果接收到的包号和期望接收的包号匹配，则缓存数据
            if pack_number == expected_pack_number:
                received_data[pack_number] = pack_data
                expected_pack_number += 1
                if pack_number == 59:
                    # 回复发送端
                    # udp_socket.sendto(b"ok", address)
                    break

        except socket.timeout:
            # 超时表示数据接收完成或发生了丢包
            break

    # 组装接收到的数据包
    received_bytes = b"".join(received_data[i] for i in range(expected_pack_number))

    return received_bytes


def create_tcp(host, port) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("socket created. Prototype: TCP")

    try:
        s.bind((host, port))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print('socket bind successfully.')

    s.listen(10)
    print('socket now listening... Host: ' + host + ' Port: ' + str(port))
    return s


def create_udp(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_socket.bind((host, port))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('socket created successfully\n Host: ' + host + ' Port: ' + str(port))


def connect_tcp(address: tuple) -> socket.socket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print("socket created. Prototype: TCP")
    while True:
        try:
            s.connect(address)
        except TimeoutError:
            continue
        except socket.error as msg:
            print('Connect failed.' + str(msg))
            continue
        break
    # print('socket connected to ' + address[0] + ':' + str(address[1]))
    return s
