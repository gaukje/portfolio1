import argparse
import sys
import threading
import time
from socket import *


# Utility functions
# parse_num_bytes(num_str): Converts a number string with a unit (B, KB, MB) to its corresponding integer value in bytes.
def parse_num_bytes(num_str):
    units = {'B': 1, 'KB': 1000, 'MB': 1000 * 1000}
    last_char = num_str[-1]
    if last_char in units:
        num = int(num_str[:-1]) * units[last_char]
    else:
        num = int(num_str)
    return num

# format_summary_line(headers, data): Formats a summary line for printing, with the columns aligned based on the maximum width of each column.
def format_summary_line(headers, data):
    max_widths = [max(map(len, col)) for col in zip(headers, data)]
    return " ".join((val.ljust(width) for val, width in zip(data, max_widths)))


# Server functions
# server(server_ip, server_port, format_unit): Sets up a server listening on the given IP and port, and accepts incoming connections. For each connection, a new thread is started to handle the client.
def server(server_ip, server_port, format_unit):
    try:
        with socket(AF_INET, SOCK_STREAM) as server_socket:
            server_socket.bind((server_ip, server_port))
            server_socket.listen(5)

            print(f"---------------------------------------------")
            print(f"A simpleperf server is listening on port {server_port}")
            print(f"---------------------------------------------")

            while True:
                connection, client_address = server_socket.accept()
                client_thread = threading.Thread(target=handle_client, args=(connection, client_address, format_unit))
                client_thread.start()

    except ConnectionError as e:
        print(f"Failed to connect to server: {e}")


#handle_client(connection, client_address, format_unit): Receives data from the client, calculates the received data size and bandwidth, and prints a summary.
def handle_client(connection, client_address, format_unit):
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
    received_data = received_bytes / format_unit['divisor']
    bandwidth = received_data / time_elapsed

    # Modify the summary line to use format_unit
    summary = f"Received {received_data:.2f} {format_unit['unit']} in {time_elapsed:.2f} seconds\n" \
              f"Bandwidth: {bandwidth:.2f} {format_unit['unit']}/s"
    print(summary)


# Client functions
# client(server_ip, server_port, duration, interval, parallel, num_bytes=None): Starts the client, which creates the specified number of parallel connections to the server and sends data.
def client(server_ip, server_port, duration, interval, parallel, message_size, format_unit, num_bytes=None):

    try:
        threads = []
        for _ in range(parallel):
            t = threading.Thread(target=client_worker, args=(
            server_ip, server_port, duration, interval, format_unit, message_size, num_bytes))

            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    except ConnectionError as e:
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)

# client_worker(server_ip, server_port, duration, interval, message_size, num_bytes=None): Connects to the server, sends data to it for the given duration, and prints statistics at specified intervals.
def client_worker(server_ip, server_port, duration, interval, format_unit, message_size, num_bytes=None):
    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port))

            print("---------------------------------------------")
            print(f"A simpleperf client connecting to server {server_ip}, port {server_port}")
            print("---------------------------------------------")
            print(f"Client connected with {server_ip} port {server_port}")

            sent_bytes = 0
            prev_sent_bytes = 0
            start_time = time.time()
            last_interval_time = start_time


            while (time.time() - start_time < duration) and (num_bytes is None or sent_bytes < num_bytes):
                data = b'0' * message_size
                client_socket.sendall(data)
                sent_bytes += len(data)

                if interval and time.time() - last_interval_time >= interval:
                    print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, interval, format_unit,
                                   prev_sent_bytes)
                    prev_sent_bytes = sent_bytes  # Update the prev_sent_bytes value
                    last_interval_time = time.time()

            print_interval(client_socket, start_time, sent_bytes, server_ip, server_port,
                           time.time() - last_interval_time, format_unit, prev_sent_bytes)

            client_socket.sendall(b"BYE")
            ack = client_socket.recv(1024)

            if ack == b"ACK:BYE":
                end_time = time.time()
                time_elapsed = end_time - start_time
                print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, time_elapsed, format_unit,
                               summary=True)
    except ConnectionError as e:
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)

# print_interval(...): Prints the statistics for a given interval, including bandwidth and the amount of data transferred.
def print_interval(client_socket: socket, start_time: float, sent_bytes: int, server_ip: str, server_port: int, interval: float, format_unit: dict, prev_sent_bytes: int = 0, summary=False):
    time_elapsed = time.time() - start_time
    interval_start = time_elapsed - interval
    sent_data = sent_bytes / format_unit['divisor']
    sent_data_interval = (sent_bytes - prev_sent_bytes) / format_unit['divisor']
    bandwidth = sent_data_interval / interval

    headers = ["ID", "Interval", "Transfer", "Bandwidth"]
    data_row = [
        f"{server_ip}:{server_port}",
        f"{interval_start:.2f} - {time_elapsed:.2f}",
        f"{sent_data:.2f} {format_unit['unit']}",
        f"{bandwidth:.2f} {format_unit['unit']}/s"
    ]

    if summary:
        print("----------------------------------------------------")
    else:
        table_data = [headers, data_row]
        max_widths = [max(map(len, col)) for col in zip(*table_data)]

        for row in table_data:
            print(" ".join((val.ljust(width) for val, width in zip(row, max_widths))))



# parse_format_unit(format_unit): Parses the format unit string and returns a dictionary with the unit and its corresponding divisor.
def parse_format_unit(format_unit):
    units = {'B': 1, 'KB': 1000, 'MB': 1000 * 1000}
    return {'unit': format_unit, 'divisor': units[format_unit]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf tool")

    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-c", "--client", action="store_true", help="enable the client mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB",
                        help="format of summary of results")
    parser.add_argument("-I", "--server_ip", type=str, default="127.0.0.1", help="IP address of the server")
    parser.add_argument("-t", "--time", type=int, default=25, help="Total duration for which data should be generated")
    parser.add_argument("-i", "--interval", type=int, default=None, help="print statistics per z second")
    parser.add_argument("-n", "--num", type=str, help="Number of bytes")
    parser.add_argument("-P", "--parallel", type=int, choices=range(1, 6), default=1,
                        help="creates parallel connections to connect to the server and send data - it must be 1 and "
                             "the max value should be 5 - default:1")
    parser.add_argument("-m", "--message_size", type=int, default=1000,
                        help="Number of bytes in each message sent by the client")

    args = parser.parse_args()

    if args.server:
        format_unit = parse_format_unit(args.format)
        server(args.bind, args.port, format_unit)
    elif args.client:
        if args.num:
            num_bytes = parse_num_bytes(args.num)
        else:
            num_bytes = None
        format_unit = parse_format_unit(args.format)
        client(args.server_ip, args.port, args.time, args.interval, args.parallel, args.message_size, format_unit, num_bytes)

    else:
        print("Please specify server mode with -s or --server")

    # Need to specify units with the -f flag on when running the client aswell