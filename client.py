import socket
import argparse
from socket import *

def client(ip, port, path):
    # Open file for reading
    with open(path, 'rb') as file:
        # Creating TCP socket and connecting to server
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((ip, port))

        # Sending content in chunks of 1000 bytes
        message = 0
        while true:
            data = file.read(1000)
            if not data:
                break
            clientSocket.send(data)
            message += len(data)

        # Receiving acknowledgement message from server
        ack = clientSocket.recv(1000)
