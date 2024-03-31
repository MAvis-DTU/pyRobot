import socket
import numpy as np
from PIL import Image
import io
import cv2
import matplotlib.pyplot as plt
import paramiko
import signal
import sys

import re

# SSH connection parameters
host = "192.168.1.108"
username = "nao"
password = "Sokrates1"
global RUNNING
RUNNING = True

# SSH command to run the ./pepper_cameras script
ssh_command = './pepper_cameras'

# Establish SSH connection and run the command
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(host, password=password, username=username)
# Function to handle termination signal
def signal_handler(sig, frame):
    print("Terminating server...")
    # Send cotermination command via SSH
    ssh_client.exec_command("killall pepper_cameras")
    ssh_client.close()
    print("Server terminated.")
    global RUNNING
    RUNNING = False
    sys.exit(0)
    
# Register signal handler for interrupt signals
signal.signal(signal.SIGINT, signal_handler)

stdin, stdout, stderr = ssh_client.exec_command(ssh_command, get_pty=True)
output = []
for i, line in enumerate(iter(stdout.readline, "")):
    if i == 6:
        print(line, end="")
        port = ''.join(re.findall(r'\d+', line))
        port = int(''.join(map(str, port)))
        break

# Loop to receive and display images
while RUNNING:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    try:
        remaining = int.from_bytes(client_socket.recv(4), byteorder='little')
        image_data = bytearray()
        while remaining > 0:
            data = client_socket.recv(remaining)
            remaining -= len(data)
            image_data += data
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    except:
        continue
    cv2.imshow("Result", image)
    cv2.waitKey(1)