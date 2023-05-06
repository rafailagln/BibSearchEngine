import socket
import struct


def receive_message(conn):
    """Receive a message over the socket."""
    header = conn.recv(4)
    if not header:
        return None
    message_size = struct.unpack('!I', header)[0]
    message_chunks = []
    remaining_size = message_size
    while remaining_size > 0:
        chunk_size = min(remaining_size, 4096)
        chunk = conn.recv(chunk_size)
        print(f"Received chunk length: {len(chunk)}")
        if not chunk:
            break
        message_chunks.append(chunk)
        remaining_size -= len(chunk)
    message = b''.join(message_chunks).decode()
    print("[+] Message received successfully")
    return message


if __name__ == '__main__':

    # Define the host and port to connect to
    HOST = '127.0.0.1'
    PORT = 8080

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"[*] Listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    print(f"[*] Connected to {addr[0]}:{addr[1]}")
    message = receive_message(conn)
    print(f"Received message: {message}")
    print(f"Received message length: {len(message)}")
    conn.close()
    s.close()
