import gzip
import json
import os
import socket
import struct
import ssl
import sys


def count_documents_in_files(folder_path):
    total_documents = 0

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a gzipped JSON file
        if filename.endswith('.gz'):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)

            # Unzip the gzipped JSON file and load the data
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                json_data = json.load(f)

            # Count the documents in the current JSON file
            total_documents += len(json_data['items'])

    return total_documents


# request without SSL encryption
# def send_request(node_addr, request):  # send in chunks
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.connect(node_addr)
#         sock.sendall(json.dumps(request).encode())
#         response = sock.recv(10000).decode()
#
#         try:
#             return json.loads(response)
#         except json.JSONDecodeError as e:
#             print(f"Failed to decode JSON response: {e}")
#             return None

def send_request(node_addr, request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(node_addr)
        send_message(json.dumps(request), sock)
        response = receive_message(sock)

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            # return ""
            return None

# request with SSL encryption
# def send_request(node_addr, request):
#     context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#     context.load_verify_locations('/home/giannis-pc/Desktop/BibSearchEngine/src/back/distributed/key/cert.pem')
#
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         with context.wrap_socket(sock, server_hostname='localhost') as ssock:
#             ssock.connect(node_addr)
#             ssock.sendall(json.dumps(request).encode())
#             response = ssock.recv(10000).decode()
#
#             try:
#                 return json.loads(response)
#             except json.JSONDecodeError as e:
#                 print(f"Failed to decode JSON response: {e}")
#                 return None


def send_message(message, conn):
    """Send a message over the socket."""
    message_size = len(message)
    print(f"[+] Message length:", message_size)
    sys.stdout.flush()
    header = struct.pack('!I', message_size)
    conn.sendall(header)
    conn.sendall(message.encode())
    print(f"[+] Message sent successfully")


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
