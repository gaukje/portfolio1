This script is a simple network performance measurement tool that supports server and client modes for data transmission
and reception. The functions work together to parse command-line arguments, set up server and client sockets, handle 
incoming connections, send data, calculate bandwidth and time elapsed, and format and print output. The script can
be used by first running it in server mode on one machine and then running it in client mode on another machine, 
specifying the required command-line arguments for configuring IP addresses, ports, format units, duration, intervals, 
parallel connections, and message sizes.

This script is a simple performance measurement tool that can be used for network testing. It supports both server and 
client modes, allowing for the transmission and reception of data over a network.

Key Functions
parse_num_bytes(num_str)

This function takes a string representing a number of bytes and converts it into an integer. The string can include 
units such as B (bytes), KB (kilobytes), and MB (megabytes). It returns the number of bytes as an integer.
format_summary_line(headers, data)

This function formats a summary line for the output. It takes a list of headers and a list of data values, aligns them, 
and returns a formatted string.
server(server_ip, server_port, format_unit)

This function sets up a server socket to listen for incoming connections. When a connection is accepted, it creates a 

new thread to handle the client using the handle_client() function.
handle_client(connection, client_address, format_unit)

This function handles a client connection. It continuously receives data from the client and calculates the amount of 
data received, bandwidth, and time elapsed. When the connection is closed, it prints a summary of the data transfer.
client(server_ip, server_port, duration, interval, parallel, message_size, format_unit, num_bytes)

This function initiates the client mode. It creates a specified number of parallel connections to the server and sends 
data. The data transmission continues for a given duration or until the specified number of bytes has been sent.
client_worker(server_ip, server_port, duration, interval, format_unit, message_size, num_bytes)

This function is responsible for connecting to the server and continuously sending data until the specified duration or 
number of bytes has been reached. It also prints statistics at specified intervals.

"print_interval(client_socket, start_time, sent_bytes, server_ip, server_port, interval, format_unit, prev_sent_bytes, summary)

This function prints the data transfer statistics in a formatted table at specified intervals. It can also print a 
summary line when the data transfer is complete.

parse_format_unit(format_unit)

This function converts a unit string (B, KB, or MB) into a dictionary containing the unit string and its corresponding divisor.
positive_int(value)

This function is used in the argument parser to check if a provided value is a positive integer.
Command-Line Arguments

The script accepts several command-line arguments for configuring server and client modes, IP addresses, ports, format 
units, duration, intervals, parallel connections, message sizes, and more.
Usage

To use this script, first run it in server mode on the machine that will act as the server. Then, run it in client mode 
on the machine that will act as the client. The script will send data between the client and server and provide 
performance statistics.

Please note that you need to specify the format units with the -f flag when running both the server and the client.