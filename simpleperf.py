import socket
import threading
import time
import argparse


def handle_client(client_socket, client_address):
    # Receive the data in chunks of 1000 bytes and calculate the amount of data received
    start_time = time.time()
    received_data = 0
    while True:
        data = client_socket.recv(1000)
        if not data:
            break
        received_data += len(data)

    # Calculate the bandwidth and print the result
    elapsed_time = time.time() - start_time
    bandwidth = received_data / elapsed_time / (1024 * 1024)
    print("Received {:.2f} MB from {} in {:.2f} seconds ({:.2f} Mbps)".format(
        received_data / (1024 * 1024), client_address, elapsed_time, bandwidth))

    # Send the acknowledgement message to the client
    client_socket.send("ACK:BYE".encode())

    # Close the client socket
    client_socket.close()


def server_mode(ip_address, port_number, file_size):
    # Create a TCP socket and bind it to the IP address and port number
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port_number))

    # Listen for incoming connections
    server_socket.listen(5)
    print("Server is listening on {}:{}".format(ip_address, port_number))

    while True:
        # Accept the incoming connection and create a new thread to handle it
        client_socket, client_address = server_socket.accept()
        print("Client {} is connected".format(client_address))
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

    # Close the server socket
    server_socket.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TCP server for receiving data from clients')
    parser.add_argument('ip_address', type=str, help='IP address to bind the server socket to')
    parser.add_argument('port_number', type=int, help='Port number to bind the server socket to')
    args = parser.parse_args()

    server_mode(args.ip_address, args.port_number, 0)