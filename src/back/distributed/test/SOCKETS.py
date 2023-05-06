import socket

# Define the host and port to bind the socket
HOST = '127.0.0.1'
PORT = 8080


def send_file(filename, conn):
    """Send a file over the socket."""
    with open(filename, 'rb') as f:
        file_data = f.read(1024)  # Read file in chunks
        while file_data:
            conn.send(file_data)
            file_data = f.read(1024)

        print("[+] File sent successfully")


# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

# Listen for incoming connections
s.listen(1)
print(f"[*] Listening on {HOST}:{PORT}")

# Accept a client connection
conn, addr = s.accept()
print(f"[*] Connected to {addr[0]}:{addr[1]}")

# Send a file
filename = 'example.txt'
send_file(filename, conn)

# Close the connection and socket
conn.close()
s.close()
