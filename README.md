
    Import necessary libraries:
    The code imports the required libraries for sockets, threading, argparse (for command-line argument parsing), and the time module.

    Utility functions:
        parse_num_bytes: Parses a string representing a number of bytes, and returns the corresponding integer value (e.g., "10M" -> 10,000,000).
        format_summary_line: Formats the data for printing as a table row by adjusting the column widths.

    Server functions:
        server: The main function for server mode. It creates a socket, binds it to the given IP and port, and listens for incoming connections. When a client connects, it starts a new thread to handle that client using the handle_client function.
        handle_client: This function is the target for each client-handling thread. It receives data from the client, tracks the received bytes, and calculates the time elapsed. When the client sends the "BYE" message, it sends an acknowledgment and closes the connection. Finally, it prints a summary of the received data and bandwidth.

    Client functions:
        client: The main function for client mode. It creates and starts multiple threads (parallel number of threads) that will send data to the server. After starting all the threads, it waits for them to finish using t.join().
        client_worker: The target function for each thread created in the client function. It establishes a connection with the server, sends data in chunks of 1000 bytes, and tracks the sent bytes and time elapsed. It also handles the intervals by calling the print_interval function when the specified interval has passed. At the end, it sends a "BYE" message to the server to signal the end of the connection, and then prints the final summary using print_interval.
        print_interval: This function prints the statistics for each interval. It calculates the time elapsed since the start time, the interval start, and the sent megabytes and bandwidth for the interval. It then prints the interval statistics in the desired format. If the summary flag is True, it prints a separator line instead of the table headers.

    Argument parsing and main code execution:
        The code defines an argparse.ArgumentParser instance to handle command-line arguments, with options for server and client modes, IP addresses, port numbers, time intervals, number of bytes to send, and parallel connections.
        Based on the parsed arguments, the code either starts the server mode with the server function or the client mode with the client function.

This code provides a simple tool for measuring network performance by sending data between a client and a server, with options for specifying the number of bytes to send, the interval to print statistics, and the number of parallel connections.

Here’s a short summary of the building blocks that simpleperf consists of. 

Argument parsing: The script utilizes the built-in “argparse” module to parse command-line arguments, allowing user to specify which mode they want to run the program in, in addition to various parameters such as duration, number of parallel connections, unit (B, KB, MB), etc.

Socket: The program uses Python’s “socket” module to create and manage connections. The server listens for incoming connections using a “SOCK_STREAM” socket, while the client creates a “SOCK_STREAM” socket to connect to the server.

Server: The server function listens for incoming connections and creates a new thread to handle each client that wishes to connect by using the handle_client function. This function receives data from the client. Tracks the number of received bytes, and calculates the bandwidth and time elapsed for the connection. The server continues to accept new connections until it’s manually terminated.

Client:  The client function is able to create parallel connections to the server based on the specified number of parallel connections. It uses the client_worker function to send data to the server continuously for the given duration or until the specified number of bytes is sent. The client tracks the number of sent bytes and prints the bandwidth statistics at specified intervals.

Message: The client send messages of a specified size. Additionally the client can print statistics at regular intervals.

Format: The parse_format_unit function is responsible for parsing the data format specified by the user and returning the appropriate unit and divisor for calculations.

Termination: The client sends a “BYE” message to the server after specified duration or when the specified number of bytes is met. The server acknowledges the “BYE” message by sending an “ACK:BYE” message back to the client. Both the server and the client then close their socket connections.
