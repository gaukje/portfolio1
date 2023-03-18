import argparse
from socket import *
import time


def client(serverIp, serverPort, duration):
    # Creating socket and connecting to the server
    with socket(AF_INET, SOCK_STREAM) as clientSocket:
        clientSocket.connect((serverIp, serverPort))  # Automatically closes the socket when the block is exited

        print("---------------------------------------------")
        print(f"A simpleperf client connecting to server {serverIp}, port {serverPort}")
        print("---------------------------------------------")
        print(f"Client connected with {serverIp} port {serverPort}")

        sentBytes = 0
        startTime = time.time()

        # Send data for the specified duration
        while time.time() - startTime < duration:
            data = b'0' * 1000
            clientSocket.sendall(data)
            sentBytes += len(data)

        # Sending a 'BYE' message and waiting for acknowledgement
        clientSocket.sendall(b"BYE")
        ack = clientSocket.recv(1024)

        if ack == b"ACK:BYE":
            endTime = time.time()
            timeElapsed = endTime - startTime

            sentMB = sentBytes / 1000 / 1000
            bandwidthMPBS = sentMB / timeElapsed

            print(f"ID Interval Transfer Bandwidth")
            print(f"{serverIp}:{serverPort} 0.0 - {timeElapsed:.2f} {sentMB:.2f} MB {bandwidthMPBS:.2f} Mbps")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf client")

    parser.add_argument("-c", "--client", action="store_true", help="enable the client mode")
    parser.add_argument("-I", "--server_ip", type=str, help="IP address of the server")
    parser.add_argument("-p", "--server_port", type=int, help="port number of the server")
    parser.add_argument("-t", "--time", type=int, help="total duration in seconds to send data")

    args = parser.parse_args()

    if args.client:
        if args.server_ip and args.server_port and args.time:
            client(args.server_ip, args.server_port, args.time)
        else:
            print("Please specify server IP, server port, and duration using -I, -p, and -t options")
    else:
        print("Please specify client mode with -c or --client")
