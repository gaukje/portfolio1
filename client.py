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
        while True:
            data = file.read(1000)
            if not data:
                break
            clientSocket.send(data)
            message += len(data)

        # Receiving acknowledgement message from server
        ack = clientSocket.recv(1000)

        # Print the result
        print("Sent {:.2f} MB to {}:{} and received acknowledgement: {}".format(
             message / (1000 * 1000), ip, port, ack.decode()))

        # Close the client socket
        clientSocket.close()


if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='TCP client for sending data to the server')
        parser.add_argument('ip', type=str, help='IP address')
        parser.add_argument('port', type=int, help='Port number')
        parser.add_argument('path', type=str, help='Path of the file you wish to send')
        args = parser.parse_args()

        client(args.ip, args.port, args.path)