import argparse
import socket
import time


def server(host, port):
    # Create a socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the specified host and port
    serverSocket.bind((host, port))

    # Listen for incoming connections
    serverSocket.listen(1)

    print(f"---------------------------------------------")
    print(f"A simpleperf server is listening on port {port}")
    print(f"---------------------------------------------")

    # Accept a connection
    connection, client_address = serverSocket.accept()

    total_received_bytes = 0
    start_time = time.time()

    try:
        while True:
            # Receive data in chunks of 1000 bytes
            data = connection.recv(1000)
            total_received_bytes += len(data)

            if not data:
                break

    finally:
        end_time = time.time()
        connection.close()

        elapsed_time = end_time - start_time
        received_kilobytes = total_received_bytes / 1000
        received_megabytes = received_kilobytes / 1000

        bandwidth_kbps = received_kilobytes / elapsed_time
        bandwidth_mbps = received_megabytes / elapsed_time

        print(f"Received {received_megabytes:.2f} MB in {elapsed_time:.2f} seconds")
        print(f"Bandwidth: {bandwidth_kbps:.2f} Kbps ({bandwidth_mbps:.2f} Mbps)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf server")

    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB", help="format of summary of results")

    args = parser.parse_args()

    if args.server:
        server(args.bind, args.port)
    else:
        print("Please specify server mode with -s or --server")
