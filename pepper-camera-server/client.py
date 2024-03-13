import socket
import numpy as np
from PIL import Image
import io
import cv2
import matplotlib.pyplot as plt

while True:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.1.108', 12345))

    remaining = int.from_bytes(client_socket.recv(4), byteorder='little')
    image_data = bytearray()
    while remaining > 0:
        data = client_socket.recv(remaining)
        remaining -= len(data)
        image_data += data

    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    cv2.imshow("Result", image)
    cv2.waitKey(1)