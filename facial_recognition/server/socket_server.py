import socket
import sys
import cv2
import pickle
import numpy as np
import struct
import zlib


HOST = '127.0.0.1'
PORT = 8485

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'Socket created in port {PORT}')

s.bind((HOST, PORT))
print('Socket bind complete')
s.listen(10)
print('Socket now listening')

conn, address = s.accept()

data = b''
payload_size = struct.calcsize('>L')
print(f'Payload Size: {payload_size}')

while True:
    client_socket, client_address = s.accept()
    if client_socket:
        print(f'Connection found: {client_address}')

    data = client_socket.recv(1024)
    print(f'From client_address: {client_address}, received: {data}')

    while len(data) < payload_size:
        print(f'Recovered: {len(data)}')
        data += conn.recv(4096)

    print(f'Done Recv: {len(data)}')
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack('>L', packed_msg_size)[0]
    print(f'msg_size: {msg_size}')

    while len(data) < msg_size:
        data += conn.recv(4096)

    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    cv2.imshow('Video from socket', frame)
    cv2.waitKey(1)

cv2.destroyAllWindows()
