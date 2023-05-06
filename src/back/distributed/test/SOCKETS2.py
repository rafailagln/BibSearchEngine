import socket

# Define the host and port to connect to
HOST = '127.0.0.1'
PORT = 8080


def receive_file(filename, conn):
    """Receive a file over the socket."""
    with open(filename, 'wb') as f:
        file_data = conn.recv(1024)
        while file_data:
            f.write(file_data)
            file_data = conn.recv(1024)

        print("[+] File received successfully")


# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
s.connect((HOST, PORT))

# Receive a file
filename = 'received_example.txt'
receive_file(filename, s)

# Close the connection and socket
s.close()
