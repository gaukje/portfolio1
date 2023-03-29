import argparse
import sys
import threading
import time
from socket import *

# This is the main script for Simpleperf, a simplified version of iPerf for measuring network throughput.

# Utility functions

# Converts a number string with a unit (B, KB, MB) to its corresponding integer value in bytes.
# Arguments: num_str (string) - A string containing the number and its unit (e.g. '10MB')
# Returns: num (int) - The integer value of the number in bytes.
def parse_num_bytes(num_str):
    units = {'B': 1, 'K': 1000, 'M': 1000 * 1000}
    last_char = num_str[-1]
    if last_char in units:
        num = int(num_str[:-1]) * units[last_char]
    else:
        num = int(num_str)
    return num

# Formats a summary line for printing, with the columns aligned based on the maximum width of each column.
# Arguments: headers (list) - A list of strings containing the column headers.
#            data (list) - A list of strings containing the data to be printed.
# Returns: summary (string) - A string containing the formatted summary line.
def format_summary_line(headers, data):
    max_widths = [max(map(len, col)) for col in zip(headers, data)]
    return " ".join((val.ljust(width) for val, width in zip(data, max_widths)))


# Server functions

# Sets up a server listening on the given IP and port, and accepts incoming connections. For each connection, a new
# thread is started to handle the client.
# Arguments: server_ip (string) - The IP address of the server.
#            server_port (int) - The port number on which the server should listen.
#            format_unit (dict) - A dictionary containing the format unit and its corresponding divisor.
# Returns: None.
def server(server_ip, server_port, format_unit):
    # Set up socket and listen for incoming connections
    try:
        # Set up socket and listen for incoming connections
        with socket(AF_INET, SOCK_STREAM) as server_socket:
            server_socket.bind((server_ip, server_port))
            server_socket.listen(5)

            print(f"---------------------------------------------")
            print(f"A simpleperf server is listening on port {server_port}")
            print(f"---------------------------------------------")

            # Accept incoming connections and receive data
            while True:
                connection, client_address = server_socket.accept()
                # create a new thread to handle each client connection
                client_thread = threading.Thread(target=handle_client, args=(connection, client_address, format_unit))
                client_thread.start()

    except ConnectionError as e:
        print(f"Failed to connect to server: {e}")


# Receives data from the client, calculates the received data size and bandwidth, and prints a summary.
# Arguments: connection (socket) - The socket object representing the client connection.
#            client_address (tuple) - A tuple containing the client's IP address and port number.
#            format_unit (dict) - A dictionary containing the format unit and its corresponding divisor.
# Returns: None.
def handle_client(connection, client_address, format_unit):
    # Initialize variables to track received data and time elapsed
    received_bytes = 0
    start_time = time.time()

    # Continuously receive data from the client until the BYE message is received
    while True:
        data = connection.recv(1000)
        if data == b"BYE":
            # Send an acknowledgement message and break out of the loop
            connection.sendall(b"ACK:BYE")
            break

        # Add the length of the received data to the total number of received bytes
        received_bytes += len(data)

    # Get the time elapsed since the start of the connection and close the socket
    end_time = time.time()
    connection.close()

    # Calculate the amount of data received, bandwidth, and time elapsed
    time_elapsed = end_time - start_time
    received_data = received_bytes / format_unit['divisor']
    bandwidth = received_data / time_elapsed

    # Modify the summary line to use format_unit
    summary = f"Received {received_data:.2f} {format_unit['unit']} in {time_elapsed:.2f} seconds\n" \
              f"Bandwidth: {bandwidth:.2f} {format_unit['unit']}/s"
    # Print the summary line
    print(summary)


# Client functions
# client(server_ip, server_port, duration, interval, parallel, num_bytes=None):
# Starts the client, which creates the specified number of parallel connections to the server and sends data.
# Arguments:
# - server_ip (string): IP address of the server.
# - server_port (int): Port number on which the server is listening.
# - duration (int): Total duration for which data should be generated.
# - interval (int): Print statistics per z second.
# - parallel (int): Number of parallel connections to the server.
# - message_size (int): Number of bytes in each message sent by the client.
# - format_unit (dict): A dictionary containing the format unit and its corresponding divisor.
# - num_bytes (int or None): Number of bytes to transfer. If None, the transfer is indefinite.
# Returns: None.
def client(server_ip, server_port, duration, interval, parallel, message_size, format_unit, num_bytes=None):

    try:
        threads = []
        for _ in range(parallel):
            # Start a new thread for each connection to the server
            t = threading.Thread(target=client_worker, args=(
            server_ip, server_port, duration, interval, format_unit, message_size, num_bytes))

            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()

    except ConnectionError as e:
        # Handle connection error and exit with status code 1
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)

# client_worker(server_ip, server_port, duration, interval, format_unit, message_size, num_bytes=None):
# Connects to the server, sends data to it for the given duration, and prints statistics at specified intervals.
# Arguments:
# - server_ip (string): IP address of the server.
# - server_port (int): Port number on which the server is listening.
# - duration (int): Total duration for which data should be generated.
# - interval (int): Print statistics per z second.
# - format_unit (dict): A dictionary containing the format unit and its corresponding divisor.
# - message_size (int): Number of bytes in each message sent by the client.
# - num_bytes (int or None): Number of bytes to transfer. If None, the transfer is indefinite.
# Returns: None.
def client_worker(server_ip, server_port, duration, interval, format_unit, message_size, num_bytes=None):
    try:
        with socket(AF_INET, SOCK_STREAM) as client_socket:
            # Connect to the server
            client_socket.connect((server_ip, server_port))

            # Print connection details
            print("---------------------------------------------")
            print(f"A simpleperf client connecting to server {server_ip}, port {server_port}")
            print("---------------------------------------------")
            print(f"Client connected with {server_ip} port {server_port}")

            # Initialize variables for tracking data transfer and time elapsed
            sent_bytes = 0
            prev_sent_bytes = 0
            start_time = time.time()
            last_interval_time = start_time

            # Continuously send data to the server until the specified duration or number of bytes has been reached
            while (time.time() - start_time < duration) and (num_bytes is None or sent_bytes < num_bytes):
                data = b'0' * message_size
                client_socket.sendall(data)
                sent_bytes += len(data)

                # Print statistics at specified intervals
                if interval and time.time() - last_interval_time >= interval:
                    print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, interval, format_unit,
                                   prev_sent_bytes)
                    prev_sent_bytes = sent_bytes  # Update the prev_sent_bytes value
                    last_interval_time = time.time()

            # Print final statistics and send a BYE message to the server to signal the end of the connection
            print_interval(client_socket, start_time, sent_bytes, server_ip, server_port,
                           time.time() - last_interval_time, format_unit, prev_sent_bytes)

            client_socket.sendall(b"BYE")
            ack = client_socket.recv(1024)

            # Print final statistics after receiving an acknowledgement message from the server
            if ack == b"ACK:BYE":
                end_time = time.time()
                time_elapsed = end_time - start_time
                print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, time_elapsed, format_unit,
                               summary=True)

    # Handle connection errors
    except ConnectionError as e:
        print(f"Connection lost during transfer: {e}")
        sys.exit(1)

# This function prints the statistics for a given interval, including bandwidth and the amount of data transferred.
# Arguments:
# - client_socket (socket): The socket object representing the client connection.
# - start_time (float): The start time of the data transfer.
# - sent_bytes (int): The number of bytes sent so far.
# - server_ip (str): The IP address of the server.
# - server_port (int): The port number of the server.
# - interval (float): The interval for which the statistics are being printed.
# - format_unit (dict): A dictionary containing the format unit and its corresponding divisor.
# - prev_sent_bytes (int): The number of bytes sent in the previous interval.
# - summary (bool): A flag indicating whether to print a summary line or not.
# Returns: None.
def print_interval(client_socket: socket, start_time: float, sent_bytes: int, server_ip: str, server_port: int, interval: float, format_unit: dict, prev_sent_bytes: int = 0, summary=False):
    # Calculate time elapsed, interval start time, and the amount of data sent in the given interval
    time_elapsed = time.time() - start_time
    interval_start = time_elapsed - interval
    sent_data = sent_bytes / format_unit['divisor']
    sent_data_interval = (sent_bytes - prev_sent_bytes) / format_unit['divisor']
    bandwidth = sent_data_interval / interval

    # Define column headers and data row for printing
    headers = ["ID", "Interval", "Transfer", "Bandwidth"]
    data_row = [
        f"{server_ip}:{server_port}",
        f"{interval_start:.2f} - {time_elapsed:.2f}",
        f"{sent_data:.2f} {format_unit['unit']}",
        f"{bandwidth:.2f} {format_unit['unit']}/s"
    ]

    # If a summary line is being printed, add a separator line before it
    if summary:
        print("----------------------------------------------------")

    # Otherwise, print the interval data in a formatted table
    else:
        table_data = [headers, data_row]
        max_widths = [max(map(len, col)) for col in zip(*table_data)]

        for row in table_data:
            print(" ".join((val.ljust(width) for val, width in zip(row, max_widths))))


# This function parses the format unit string and returns a dictionary with the unit and its corresponding divisor.
# Arguments:
# - format_unit (str): The format unit string.
# Returns:
# - A dictionary containing the unit and its corresponding divisor.
def parse_format_unit(format_unit):
    units = {'B': 1, 'KB': 1000, 'MB': 1000 * 1000}
    return {'unit': format_unit, 'divisor': units[format_unit]}


# Function that validates that the argparse argument is a positive integer.
# Returns:
# - Error message if the argument is negative
# - The integer value if the argument is correct
def positive_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simpleperf tool")

    # Parse command line arguments
    parser.add_argument("-s", "--server", action="store_true", help="enable the server mode")
    parser.add_argument("-c", "--client", action="store_true", help="enable the client mode")
    parser.add_argument("-b", "--bind", type=str, default="0.0.0.0", help="IP address of the server's interface")
    parser.add_argument("-p", "--port", type=int, default=8080, help="port number on which the server should listen")
    parser.add_argument("-f", "--format", type=str, choices=["B", "KB", "MB"], default="MB",
                        help="format of summary of results")
    parser.add_argument("-I", "--server_ip", type=str, default="127.0.0.1", help="IP address of the server")
    parser.add_argument("-t", "--time", type=positive_int, default=25, help="Total duration for which data should be generated")
    parser.add_argument("-i", "--interval", type=positive_int, default=None, help="print statistics per z second")
    parser.add_argument("-n", "--num", type=str, help="Number of bytes")
    parser.add_argument("-P", "--parallel", type=int, choices=range(1, 6), default=1,
                        help="creates parallel connections to connect to the server and send data - it must be 1 and "
                             "the max value should be 5 - default:1")
    parser.add_argument("-m", "--message_size", type=int, default=1000,
                        help="Number of bytes in each message sent by the client")

    # Parse command-line arguments
    args = parser.parse_args()

    if args.server:
        # Start the server
        format_unit = parse_format_unit(args.format)
        server(args.bind, args.port, format_unit)
    elif args.client:
        if args.num:
            # Parse number of bytes if specified
            num_bytes = parse_num_bytes(args.num)
        else:
            num_bytes = None
        format_unit = parse_format_unit(args.format)
        # Start the client
        client(args.server_ip, args.port, args.time, args.interval, args.parallel, args.message_size, format_unit, num_bytes)

    else:
        print("Please specify server mode with -s or --server")

    # Need to specify units with the -f flag on when running the client aswell

    """
    The main function parses the command-line arguments using argparse.ArgumentParser, and then starts the server or 
    client depending on the specified arguments. If the --server argument is specified, the server function is called 
    with the specified IP address, port number, and format unit. If the --client argument is specified, the client 
    function is called with the specified server IP address, port number, duration, interval, parallelism, message size,
    and format unit. If neither --server nor --client is specified, an error message is printed.

    The parse_num_bytes function takes a string containing a number and a unit (e.g. "10MB"), and returns the integer 
    value of the number in bytes.

    The format_summary_line function takes a list of column headers and a list of data, and returns a formatted string 
    with the columns aligned based on the maximum width of each column.
    
    The parse_format_unit function takes a string specifying the format unit (e.g. "MB"), and returns a dictionary with 
    the unit and its corresponding divisor (e.g. {'unit': 'MB', 'divisor': 1000000}).

    The server function sets up a socket and listens for incoming connections. For each connection, a new thread is 
    started to handle the client using the handle_client function.
    
    The handle_client function receives data from the client, calculates the received data size and bandwidth, and 
    prints a summary.
    
    The client function starts the client, which creates the specified number of parallel connections to the server and 
    sends data. It creates a separate thread for each connection using the client_worker function.
    
    The client_worker function connects to the server, sends data to it for the given duration, and prints statistics 
    at specified intervals.
    
    The print_interval function prints the statistics for a given interval, including bandwidth and the amount of 
    data transferred.
    
    Overall, the Simpleperf tool provides a simple way to measure network throughput using either a server or 
    client mode. It supports specifying various parameters such as IP address, port number, duration, interval, 
    parallelism, message size, and format unit. The tool uses threads to handle multiple connections in parallelism, 
    message size, and format unit. The tool uses threads to handle multiple connections in parallel and prints 
    statistics at specified intervals to monitor network performance.
    """