import heapq
import json
import socket
import ssl
import time
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from hashlib import sha256

from Indexer.IndexCreator import IndexCreator
from Ranker.Search2 import SearchEngine
from distributed.fast_json_loader import FastJsonLoader
from distributed.utils import send_request

# TODO: Check all blocking parts (see example execute_action with new thread)
# TODO: Send request in chunks like SOCKETS/SOCKETS2


def process_data(data):
    return f"Processed data: {data}"


def split_ids(ids, n):
    result = {i: [] for i in range(1, n + 1)}
    for i, _id in enumerate(ids):
        result[(i % n) + 1].append(_id)
    return result


class DistributedNode:
    def __init__(self, _node_id, _node_port, _config_file, _folder_path, _max_results, db_name, index_collection,
                 metadata_collection, _passphrase='9RXZMGoR6U%kk!H1F36%'):
        self.node_id = _node_id
        self.node_port = _node_port
        self.passphrase = _passphrase
        self.folder_path = _folder_path
        self.documents_count = {}
        self.doc_id_sequence = {}
        self.max_results = _max_results

        with open(_config_file, 'r') as f:
            config = json.load(f)

        self.neighbor_nodes = config['nodes']
        self.current_leader = None
        # self.index = TrieIndex()
        # self.index_lock = threading.Lock()
        self.db = FastJsonLoader(folder_path=self.folder_path,
                                 documents_per_file=1000,
                                 node_id=self.node_id,
                                 node_count=len(self.neighbor_nodes))
        self.indexer = IndexCreator(self.db,
                                    db_name=db_name,
                                    index_collection=index_collection,
                                    metadata_collection=metadata_collection)
        self.engine = SearchEngine(self.indexer, max_results=10000)
        self.db.doc_id = self.node_id
        self.db.node_count = len(config['nodes'])

    def handle_request(self, request):
        data = json.loads(request)
        action = data.get('action', '')

        with ThreadPoolExecutor(max_workers=1) as executor:
            if action == 'insert':
                executor.submit(self.handle_insert, data)
                return json.dumps({'status': 'Thread started'})
            elif action == 'search':
                if data['forwarded']:
                    self.handle_search(data)
                    return json.dumps({'status': 'OK'})
                else:
                    executor.submit(self.handle_search, data)
                    return json.dumps({'status': 'Thread started'})
            elif action == 'delete':
                executor.submit(self.handle_delete, data)
                return json.dumps({'status': 'Thread started'})
            elif action == 'process_data':
                return self.handle_process_data(data)
            elif action == 'heartbeat':
                return json.dumps({'status': 'OK'})
            elif action == 'load_documents':
                self.db.load_documents()
                return json.dumps({'status': 'OK'})
            elif action == 'load_index':
                self.indexer.create_load_index()
                self.engine.bm25f.update_total_docs(self.indexer.index_metadata.total_docs)
                return json.dumps({'status': 'OK'})
            elif action == 'get_data':
                results = self.handle_get_data(data)
                return json.dumps({'status': 'OK', 'results': results})
            elif action == 'search_ids':
                results = self.search_ids(data)
                return json.dumps({'status': 'OK', 'results': results})
            elif action == 'set_starting_doc_id':
                return json.dumps({'doc_id': data.get('doc_id', ''), 'status': 'OK'})
            elif action == 'insert_docs':
                self.db.insert_documents(data.get('new_docs', ''))
                return json.dumps({'status': 'OK'})
            elif action == 'set_leader':
                self.current_leader = data['leader']
                print(f"Node {self.node_id}: Leader updated to {self.current_leader['id']}")
                return json.dumps({'status': 'OK'})
            else:
                return json.dumps({'error': 'Unknown request'})

    def handle_process_data(self, data):
        if self.current_leader['id'] != self.node_id:
            return self.forward_request(self.current_leader, data, True)
        else:
            print(f"Node {self.node_id}: Processing data")
            return json.dumps({
                'worker_id': self.node_id,
                'result': process_data(data['data'])
            })

    def get_leader(self):
        sorted_nodes = sorted(self.neighbor_nodes, key=lambda x: x['id'])
        return sorted_nodes[0]

    def update_alive_nodes(self):
        alive_nodes = []

        for _node in self.neighbor_nodes:
            if _node['id'] == self.node_id:
                alive_nodes.append(_node)
                continue

            try:
                response = send_request((_node['host'], _node['port']), {
                    'action': 'heartbeat'
                })

                if response and response.get('status') == 'OK':
                    alive_nodes.append(_node)
            except Exception as e:
                print(f"Failed to send heartbeat to node {_node['id']}: {e}")

        return alive_nodes

    def notify_nodes_of_leader(self, leader):
        for _node in self.neighbor_nodes:
            if _node['id'] != self.node_id:
                try:
                    send_request((_node['host'], _node['port']), {
                        'action': 'set_leader',
                        'leader': leader
                    })
                    print(f"Node {self.node_id}: Notified node {_node['id']} of the new leader {leader['id']}")
                except Exception as e:
                    print(
                        f"Node {self.node_id}: Failed to notify node {_node['id']} of the new leader {leader['id']}."
                        f" {e}")

    # run without SSL encryption
    def run(self):
        with open("config.json", "r") as f:
            config = json.load(f)
            nodes = config["nodes"]

        if nodes[self.node_id - 1]['leader']:
            heartbeat_thread = threading.Thread(target=self.check_heartbeats)
            heartbeat_thread.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(('localhost', self.node_port))
            sock.listen(5)
            print(f"Node {self.node_id} listening on port {self.node_port}")

            while True:
                conn, addr = sock.accept()
                print(f"Node {self.node_id}: Connection accepted from {addr}")
                request = conn.recv(10000).decode()
                print(f"Node {self.node_id}: Received request: {request[:100]}")
                response = self.handle_request(request)
                print(f"Node {self.node_id}: Sending response: {response[:100]}")
                conn.sendall(response.encode())

    # run with encryption
    # def run(self):
    #     with open("config.json", "r") as f:
    #         config = json.load(f)
    #         nodes = config["nodes"]
    #
    #     if nodes[self.node_id - 1]['leader']:
    #         heartbeat_thread = threading.Thread(target=self.check_heartbeats)
    #         heartbeat_thread.start()
    #
    #     context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #     context.load_cert_chain(certfile="/home/giannis-pc/Desktop/BibSearchEngine/src/back/distributed/key/cert.pem",
    #                             keyfile="/home/giannis-pc/Desktop/BibSearchEngine/src/back/distributed/key/key.pem",
    #                             password=self.passphrase)
    #
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    #         sock.bind(('localhost', self.node_port))
    #         sock.listen(5)
    #         print(f"Node {self.node_id} listening on port {self.node_port}")
    #
    #         while True:
    #             conn, addr = sock.accept()
    #             print(f"Node {self.node_id}: Connection accepted from {addr}")
    #             with context.wrap_socket(conn, server_side=True) as sconn:
    #                 request = sconn.recv(10000).decode()
    #                 print(f"Node {self.node_id}: Received request: {request[:100]}")
    #                 response = self.handle_request(request)
    #                 print(f"Node {self.node_id}: Sending response: {response[:100]}")
    #                 sconn.sendall(response.encode())

    def check_heartbeats(self):
        self.execute_action('heartbeat')
        self.send_load_documents()

    def send_load_documents(self):
        # send load_documents commands to all other nodes
        self.execute_action('load_documents')
        # load documents for leader
        self.db.load_documents()
        self.send_create_index()

    def send_create_index(self):
        self.execute_action('load_index')
        # load index for leader
        self.indexer.create_load_index()
        # change total docs in bm25f for leader
        self.engine.bm25f.update_total_docs(self.indexer.index_metadata.total_docs)

    def execute_action(self, action, attr1=None, response_callback=None):
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
                        'attr1': attr1[node['id']]
                    })
                if response_callback is not None:
                    response_callback(response, node)
                if response.get('status') == 'OK':
                    successful_nodes.append(node)
                return response.get('status') == 'OK'

            except (ConnectionError, TimeoutError, OSError) as e:
                print(e)
                return False

        with ThreadPoolExecutor(max_workers=len(self.neighbor_nodes)) as executor:
            while not all_connected:
                all_ok = True
                threads = []
                for _node in self.neighbor_nodes:
                    if _node['id'] != self.node_id and _node not in successful_nodes:
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
                    self.current_leader = self.neighbor_nodes[int(self.node_id) - 1]
        print(f"Action: {action} executed!")

    def get_shard(self, key):
        num_shards = len(self.neighbor_nodes)
        shard_id = int(sha256(key.encode()).hexdigest(), 16) % num_shards
        return self.neighbor_nodes[shard_id]

    # def handle_insert(self, data):
    #     if data['forwarded']:
    #         for key, value in data['documents'].items():
    #             self.index.insert(key, value)
    #         return json.dumps({'status': 'OK'})
    #
    #     values_to_sent = {}
    #
    #     for key, value in data['documents'].items():
    #         shard = self.get_shard(key)
    #         if shard['id'] not in values_to_sent:
    #             values_to_sent[shard['id']] = {}
    #         values_to_sent[shard['id']][key] = value
    #
    #     for shard, keys in values_to_sent.items():
    #         if shard == self.node_id:
    #             with self.index_lock:
    #                 for key, value in keys.items():
    #                     self.index.insert(key, value)
    #         else:
    #             data['documents'] = keys
    #             data['forwarded'] = True
    #             self.forward_request(self.neighbor_nodes[shard - 1], data)
    #
    #     return json.dumps({'status': 'OK'})
    #
    # def handle_search(self, data):
    #     values = {}
    #     if data['forwarded']:
    #         for key in data['keys']:
    #             values[key] = self.index.search(key)[0]
    #         return json.dumps(values)
    #
    #     keys = data['keys']
    #     values_to_sent = {}
    #
    #     for key in keys:
    #         shard = self.get_shard(key)
    #         if shard['id'] not in values_to_sent:
    #             values_to_sent[shard['id']] = []
    #         values_to_sent[shard['id']].append(key)
    #
    #     for shard, keys in values_to_sent.items():
    #         if shard == self.node_id:
    #             for key in keys:
    #                 values[key] = self.index.search(key)
    #         else:
    #             data['keys'] = keys
    #             data['forwarded'] = True
    #             values.update(self.forward_request(self.neighbor_nodes[shard - 1], data))
    #
    #     return json.dumps({'results': values})
    #
    # def handle_delete(self, data):
    #     key = data['key']
    #     shard = self.get_shard(key)
    #
    #     if shard['id'] == self.node_id:
    #         with self.index_lock:
    #             self.index.delete(key)
    #         return json.dumps({'status': 'OK'})
    #     else:
    #         return self.forward_request(shard, data)

    def forward_request(self, node, data, to_leader=False):
        node_addr = (node['host'], node['port'])

        try:
            response = send_request(node_addr, data)
            return json.dumps(response)
        except Exception as e:
            if to_leader:
                print(f"Node {self.node_id}: Failed to forward request to leader {node['id']}. {e}")
                self.neighbor_nodes = self.update_alive_nodes()
                leader = self.get_leader()
                self.current_leader = leader
                self.notify_nodes_of_leader(leader)

                if leader['id'] == self.node_id:
                    print(f"Node {self.node_id} is now the leader")
                    return json.dumps({
                        'worker_id': self.node_id,
                        'result': process_data(data['data'])
                    })
                else:
                    print(f"Node {self.node_id}: Forwarding request to new leader {leader['id']}")
                    leader_addr = (leader['host'], leader['port'])
                    response = send_request(leader_addr, data)
                    return json.dumps(response)
            else:
                print(f"Node {self.node_id}: Failed to forward request to node {node['id']}. {e}")
                return json.dumps({'error': f"Failed to forward request to node {node['id']}"})

    def update_config(self, _config_file):
        with open(_config_file, 'w') as f:
            config = json.load(f)
            config['nodes'] = self.neighbor_nodes
            json.dump(config, f, indent=4)

    # TODO: use forward_request function instead of sending plain request
    def handle_get_data(self, data):
        ids = data.get('ids', '')
        if not data.get('forwarded'):
            results = []
            ids_per_node = split_ids(ids, self.db.node_count)
            for node, value in ids_per_node.items():
                if node == self.node_id:
                    results.extend(self.db.get_data(ids))
                else:
                    data['forwarded'] = True
                    data['ids'] = value

                    response = send_request((self.neighbor_nodes[node - 1]['host'], self.neighbor_nodes[node - 1]['port']), {
                        'action': 'get_data', 'forwarded': True, 'ids': value
                    })
                    # response = self.forward_request(self.neighbor_nodes[node - 1], data)
                    # TODO: This is overhead. Needs optimization. It returns a string and is needed to convert to JSON.
                    results.extend(json.loads(response.get('results'))['results'])
            return results
        else:
            return json.dumps({'results': self.db.get_data(ids)})

    def search_ids(self, data):
        query = data.get('query', '')
        if not data.get('forwarded'):
            results = defaultdict(float)
            for node in self.neighbor_nodes:
                if node['id'] == self.node_id:
                    results.update(self.engine.search(query))
                else:
                    data['forwarded'] = True
                    response = send_request(
                        (node['host'], node['port']), {
                            'action': 'search_ids', 'forwarded': True, 'query': query
                        })
                    # response = self.forward_request(self.neighbor_nodes[node - 1], data)
                    # TODO: This is overhead. Needs optimization. It returns a string and is needed to convert to JSON.
                    results.update(json.loads(response.get('results'))['results'])
            # return heapq.nlargest(self.max_results, results.items(), key=lambda x: x[1])
            # return results
            return list(map(int, heapq.nlargest(self.max_results, results.keys(), key=results.get)))
        else:
            return json.dumps({'results': self.engine.search(query)})



