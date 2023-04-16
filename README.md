# Simpleperf - A Simple Network Performance Tool

## Description

Simpleperf is a basic network performance tool designed to measure network throughput. It provides a server and client 
mode, allowing users to set up a server to listen for incoming connections and clients to connect and send data to 
measure performance. The tool uses Python sockets and threading to manage multiple client connections simultaneously. 
This README file provides a detailed explanation of the code, functions, and steps to run Simpleperf and generate data.

## Usage

### Server Mode

To run Simpleperf in server mode, execute the following command:
> python simpleperf.py -s

This will start a Simpleperf server that listens for incoming connections on the default IP address 0.0.0.0 and port 
8080 . You can customize the IP address and port using the -b or --bind and -p or --port options. For example:
> python simpleperf.py -s -b 192.168.1.100 -p 5001

### Client Mode

To run Simpleperf in client mode, execute the following command:
> python simpleperf.py -c

This will start a Simpleperf client that connects to a Simpleperf server running on the default IP address 127.0.0.1 and 
port 8080. You can customize the server IP address and port using the -I or --server_ip and -p or --port options, 
respectively. For example:

> python simpleperf.py -c -I 192.168.1.100 -p 9000

### Options
- -f or --format: Choose the format of the summary results (B, KB, or MB).
- -t or --time: Set the total duration (in seconds) for which data should be generated.
- -i or --interval: Print statistics per specified interval (in seconds).
- -n or --num: Set the number of bytes to send.
- -P or --parallel: Create parallel connections to the server and send data (default is 1, max value is 5).
- -m or --message_size: Set the number of bytes in each message sent by the client.

### Example with Custom Options

> python simpleperf.py -c -I 10.0.5.2 -p 8080 -f KB -t 30 -i 5

## Functions

### parse_num_bytes(num_str)
This function converts a number string with a unit (B, KB, MB) to its corresponding integer value in bytes.

### format_summary_line(headers, data)
This function formats a summary line for printing results in a neat, column-aligned manner.

### server(server_ip, server_port, format_unit)
This function sets up a Simpleperf server that listens for incoming connections on the specified IP address and port. 
It continuously accepts incoming connections and receives data, spawning a new thread to handle each client connection 
using the handle_client function.

### handle_client(connection, client_address, format_unit)
This function handles individual client connections for the server. It receives data from the client and tracks the 
received data and time elapsed. When the client sends a "BYE" message, it calculates the total data received, time taken, 
and throughput. Finally, it prints a summary of the client's performance.

### client(server_ip, server_port, format_unit, duration, interval, num_bytes, parallel, message_size)
This function sets up a Simpleperf client that connects to the specified server IP address and port. It sends data 
continuously to the server according to the specified duration, interval, number of bytes, parallel connections, and 
message size. It calculates the total data sent, time taken, and throughput, printing a summary of the client's performance.

### send_data(connection, server_address, format_unit, duration, interval, num_bytes, message_size)
This function sends data from the client to the server continuously based on the specified duration, interval, number 
of bytes, and message size. It calculates the total data sent, time taken, and throughput, printing a summary of the 
client's performance.

## Tests
To generate data using Simpleperf, you can run tests on your local machine or between two different machines connected 
to the same network.

### Local Machine Test
1. Open a terminal and run the Simpleperf server:
> python simpleperf.py -s
2. Open another terminal and run the Simpleperf client:
> python simpleperf.py -c

### Network Test
1. On Machine A (server), run the Simpleperf server:
> python simpleperf.py -s -b <IP> -p <port>
2. On Machine B (client), run the Simpleperf client: 
> python simpleperf.py -c -I <IP> -p <port>
3. Observe the generated data on both machines.

By following these steps, you can generate data using Simpleperf and analyze the network performance between the client 
and the server.