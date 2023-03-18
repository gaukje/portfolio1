"""
import argparse
import socket
import time
from socket import *


def server(serverIp, serverPort, formatUnit):
    # Create a socket
    serverSocket = socket(AF_INET, SOCK_STREAM)

    # Bind the socket to the specified host and port
    serverSocket.bind((serverIp, serverPort))

    # Listen for incoming connections
    serverSocket.listen(5)

    print(f"---------------------------------------------")
    print(f"A simpleperf server is listening on port {serverPort}")
    print(f"---------------------------------------------")

    # Accept a connection
    connection, clientAddress = serverSocket.accept()

    receivedBytes = 0
    startTime = time.time()

    try:
        while True:
            # Receive data in chunks of 1000 bytes
            data = connection.recv(1000)
            if data == b"BYE":
                connection.sendall(b"ACK:BYE")
                break

            receivedBytes += len(data)

    finally:

        endTime = time.time()
        connection.close()

        timeElapsed = endTime - startTime
        units = {
            'B': receivedBytes,
            'KB': receivedBytes / 1000,
            'MB': receivedBytes / 1000 / 1000,
        }
        receivedData = units[formatUnit]

        bandwidthUnits = {
            'B': 1,
            'KB': 1000,
            'MB': 1000 * 1000,
        }

        bandwidth = receivedBytes / timeElapsed / bandwidthUnits[formatUnit]

        summary = f"Received {receivedData:.2f} {formatUnit} in {timeElapsed:.2f} seconds\n" \
                  f"Bandwidth: {bandwidth:.2f} {formatUnit}ps"
        print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf server")

    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="format of summary of results")

    args = parser.parse_args()

    if args.server:
        server(args.bind, args.port, args.format)
    else:
        print("Please specify server mode with -s or --server")
"""