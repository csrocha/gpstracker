#!/usr/bin/python3

import socket

SERVER_HOST = socket.gethostname()
SERVER_PORT = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

data = [
    ('##,imei:359586015829802,A;', 'LOAD'),
    ('359586015829802', 'ON'),
    ('', '')
]

try:
    sock.connect((SERVER_HOST, SERVER_PORT))
    for data_send, expected in data:
        print ("Send:", data_send, "; Expected:", expected)
        sock.sendall(bytes(data_send + "\n", "utf-8"))
        received = str(sock.recv(1024), "utf-8")
        received = received.strip()
        print ("Received:", received)
        if (received != expected):
            print ("Unexpected result", received)
finally:
    sock.close()
