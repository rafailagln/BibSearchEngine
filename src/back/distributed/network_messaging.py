import struct


def send_message(message, conn):
    """Send a message over the socket."""
    message_size = len(message)
    header = struct.pack('!I', message_size)
    conn.sendall(header)
    conn.sendall(message.encode())
    print("[+] Message sent successfully")


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
        # print(f"Received chunk length: {len(chunk)}")
        if not chunk:
            break
        message_chunks.append(chunk)
        remaining_size -= len(chunk)
    message = b''.join(message_chunks).decode()
    print("[+] Message received successfully")
    return message
