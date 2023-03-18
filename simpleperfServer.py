import argparse
import time
from socket import *
import sys


def server(server_ip, server_port):
    try:
        with socket(AF_INET, SOCK_STREAM) as server_socket:
            server_socket.bind((server_ip, server_port))
            server_socket.listen(5)

            print(f"---------------------------------------------")
            print(f"A simpleperf server is listening on port {server_port}")
            print(f"---------------------------------------------")

            connection, client_address = server_socket.accept()

            received_bytes = 0
            start_time = time.time()

            while True:
                data = connection.recv(1000)
                if data == b"BYE":
                    connection.sendall(b"ACK:BYE")
                    break

                received_bytes += len(data)

            end_time = time.time()
            connection.close()

            time_elapsed = end_time - start_time
            received_data = received_bytes / 1000 / 1000
            bandwidth = received_data / time_elapsed

            summary = f"Received {received_data:.2f} MB in {time_elapsed:.2f} seconds\n" \
                      f"Bandwidth: {bandwidth:.2f} Mbps"
            print(summary)
            """
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
            """
    except ConnectionError as e:
        print(f"Failed to connect to server: {e}")


def client(server_ip, server_port, duration, interval, parallel, num_bytes=None):
    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port))

            print("---------------------------------------------")
            print(f"A simpleperf client connecting to server {server_ip}, port {server_port}")
            print("---------------------------------------------")
            print(f"Client connected with {server_ip} port {server_port}")

            sent_bytes = 0
            start_time = time.time()
            last_interval_time = start_time

            while (time.time() - start_time < duration) and (num_bytes is None or sent_bytes < num_bytes):
                data = b'0' * 1000
                client_socket.sendall(data)
                sent_bytes += len(data)

                if interval and time.time() - last_interval_time >= interval:
                    print_interval(client_socket, start_time, sent_bytes, server_ip, server_port)
                    last_interval_time = time.time()

            client_socket.sendall(b"BYE")
            ack = client_socket.recv(1024)

            if ack == b"ACK:BYE":
                end_time = time.time()
                time_elapsed = end_time - start_time

                sent_mb = sent_bytes / 1000 / 1000
                bandwidth_mbps = sent_mb / time_elapsed

                print(f"ID Interval Transfer Bandwidth")
                print(f"{server_ip}:{server_port} 0.0 - {time_elapsed:.2f} {sent_mb:.2f} MB {bandwidth_mbps:.2f} Mbps")
    except ConnectionError as e:
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)


def parse_num_bytes(num_str):
    units = {'B': 1, 'KB': 1000, 'MB': 1000 * 1000}
    last_char = num_str[-1]
    if last_char in units:
        num = int(num_str[:-1]) * units[last_char]
    else:
        num = int(num_str)
    return num

def print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, interval):
    time_elapsed = time.time() - start_time
    sent_mb = sent_bytes / 1000 / 1000
    bandwidth_mbps = sent_mb / time_elapsed

    headers = ["ID", "Interval", "Transfer", "Bandwidth"]
    data_row = [
        f"{server_ip}:{server_port}",
        f"{time_elapsed:.2f} - {time_elapsed + interval:.2f}",
        f"{sent_mb:.2f} MB",
        f"{bandwidth_mbps:.2f} Mbps"
    ]

    table_data = [headers, data_row]
    max_widths = [max(map(len, col)) for col in zip(*table_data)]

    for row in table_data:
        print(" ".join((val.ljust(width) for val, width in zip(row, max_widths))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf tool")

    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-c", "--client", action="store_true", help="enable the client mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB",
                        help="format of summary of results")
    parser.add_argument("-I", "--server_ip", type=str, help="IP address of the server")
    parser.add_argument("-t", "--time", type=int, help="Total duration for which data should be generated")
    parser.add_argument("-i", "--interval", type=int, help="print statistics per z second")
    parser.add_argument("-n", "--num", type=str, help="Number of bytes")
    parser.add_argument("-P", "--parallel", type=int, choices=range(1, 6), default=1,
                        help="creates parallel connections to connect to the server and send data - it must be 1 and the max value should be 5 - default:1")

    args = parser.parse_args()

    if args.server:
        server(args.bind, args.port)
    elif args.client:
        if args.num:
            num_bytes = parse_num_bytes(args.num)
        else:
            num_bytes = None

        client(args.server_ip, args.port, args.time, args.interval, args.parallel, num_bytes)
    else:
        print("Please specify server mode with -s or --server")
