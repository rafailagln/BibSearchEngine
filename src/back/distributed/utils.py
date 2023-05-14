import gzip
import json
import os
import socket
import struct
import sys
import time
from concurrent.futures import ThreadPoolExecutor


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
        try:
            sock.connect(node_addr)
            send_message(json.dumps(request), sock)
            response = receive_message(sock)
        except socket.error as e:
            # Re-raise the exception to propagate it further
            raise e

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            # return ""
            return None
        # TODO: check if there is error in return, if we should return None or empty []
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


def execute_action(action, neighbor_nodes, node_id, attr1=None, response_callback=None):
    all_connected = False
    successful_nodes = list()

    def send_request_wrapper(node):
        try:
            if attr1 is None:
                response = send_request((node['host'], node['port']), {
                    'action': action
                })
            else:
                response = send_request((node['host'], node['port']), {
                    'action': action,
                    'attr1': attr1
                })
            if response_callback is not None:
                response_callback(response, node)
            if response.get('status') == 'OK':
                successful_nodes.append(node)
            return response.get('status') == 'OK'

        except (ConnectionError, TimeoutError, OSError) as e:
            print(e)
            return False

    with ThreadPoolExecutor(max_workers=len(neighbor_nodes)) as executor:
        while not all_connected:
            all_ok = True
            threads = []
            for _node in neighbor_nodes:
                if not _node['alive']:
                    continue
                if _node['id'] != node_id and _node not in successful_nodes:
                    t = executor.submit(send_request_wrapper, _node)
                    threads.append(t)
            for t in threads:
                if not t.result():
                    all_ok = False
                    break
            if action == 'heartbeat':
                time.sleep(0.5)
            if all_ok:
                all_connected = True
    print(f"Action: {action} executed!")

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
