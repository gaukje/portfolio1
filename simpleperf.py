import argparse
import time
from socket import *
import sys


def server(serverIp, serverPort, formatUnit):
    try:
        with socket(AF_INET, SOCK_STREAM) as serverSocket:
            serverSocket.bind((serverIp, serverPort))
            serverSocket.listen(5)

            print(f"---------------------------------------------")
            print(f"A simpleperf server is listening on port {serverPort}")
            print(f"---------------------------------------------")

            connection, clientAddress = serverSocket.accept()

            receivedBytes = 0
            startTime = time.time()


            while True:
                data = connection.recv(1000)
                if data == b"BYE":
                    connection.sendall(b"ACK:BYE")
                    break

                receivedBytes += len(data)


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

    except ConnectionError as e:
        print(f"Failed to connect to server: {e}")

def client(serverIp, serverPort, duration):
    try:
        with socket(AF_INET, SOCK_STREAM) as clientSocket:
            clientSocket.connect((serverIp, serverPort))

            print("---------------------------------------------")
            print(f"A simpleperf client connecting to server {serverIp}, port {serverPort}")
            print("---------------------------------------------")
            print(f"Client connected with {serverIp} port {serverPort}")

            sentBytes = 0
            startTime = time.time()

            while time.time() - startTime < duration:
                data = b'0' * 1000
                clientSocket.sendall(data)
                sentBytes += len(data)

            clientSocket.sendall(b"BYE")
            ack = clientSocket.recv(1024)

            if ack == b"ACK:BYE":
                endTime = time.time()
                timeElapsed = endTime - startTime

                sentMB = sentBytes / 1000 / 1000
                bandwidthMPBS = sentMB / timeElapsed

                print(f"ID Interval Transfer Bandwidth")
                print(f"{serverIp}:{serverPort} 0.0 - {timeElapsed:.2f} {sentMB:.2f} MB {bandwidthMPBS:.2f} Mbps")
    except ConnectionError as e:
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf tool")

    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-c", "--client", action="store_true", help="enable the client mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="format of summary of results")
    parser.add_argument("-I", "--server_ip", type=str, help="IP address of the server")
    parser.add_argument("-t", "--time", type=int, help="Total duration for which data should be generated")

    args = parser.parse_args()

    if args.server and args.client:
        print("Please choose either server mode with -s or --server, or client mode with -c or --client")
    elif args.server:
        server(args.bind, args.port, args.format)
    elif args.client:
        if args.server_ip is None or args.time is None:
            print("Please provide server IP with -I or --server_ip, and duration with -t or --time")
        else:
            client(args.server_ip, args.port, args.time)
    else:
        print("Please specify server mode with -s or --server, or client mode with -c or --client")