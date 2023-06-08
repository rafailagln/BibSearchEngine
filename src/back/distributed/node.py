import argparse
import heapq
import json
import socket
import ssl
import sys
import threading
from collections import defaultdict

from hashlib import sha256

from indexer.index_creator import IndexCreator
from ranker.search import SearchEngine
from api_requester import APIRequester
from configurations.read_config import IniConfig, JsonConfig
from distributed.config_manager import ConfigManager
from distributed.fast_json_loader import FastJsonLoader
from distributed.utils import send_request, receive_message, send_message, execute_action
import concurrent.futures
from threading import Lock
from logger import MyLogger

logger = MyLogger()


def split_ids(ids, n):
    """
    Split the list of IDs into multiple shards.

    Args:
        ids (list): The list of IDs to be split.
        n (int): The number of shards.

    Returns:
        dict: A dictionary with shard IDs as keys and a list of IDs as values.
    """
    result = {i: [] for i in range(1, n + 1)}
    for i, _id in enumerate(ids):
        if _id % n == 0:
            result[n].append(_id)
        else:
            result[_id % n].append(_id)
    return result


class DistributedNode:
    def __init__(self, _node_id, _node_host, _node_port, _json_file_path, _load_folder_path, _max_results, db_name,
                 index_collection, metadata_collection, _passphrase, cert_path, key_path, api_url, api_username,
                 api_password, doc_index_metadata):
        """
        Initializes a DistributedNode object.

        Args:
            _node_id (int): The ID of the node.
            _node_host (str): The host address of the node.
            _node_port (int): The port on which the node listens for connections.
            _json_file_path (str): The path to the JSON configuration file.
            _load_folder_path (str): The path to the folder containing the documents to load.
            _max_results (int): The maximum number of search results to return.
            db_name (str): The name of the MongoDB database.
            index_collection (str): The name of the collection to store the index in MongoDB.
            metadata_collection (str): The name of the collection to store the index metadata in MongoDB.
            _passphrase (str): The passphrase for SSL encryption.
            cert_path (str): The path to the SSL certificate.
            key_path (str): The path to the SSL private key.
            api_url (str): The URL of the API.
            api_username (str): The username for API authentication.
            api_password (str): The password for API authentication.
            doc_index_metadata (str): The metadata for document indexing.

        Returns:
            None
        """

        self.results_lock = Lock()
        self.node_id = _node_id
        self.node_host = _node_host
        self.node_port = _node_port
        self.api_url = api_url
        self.api_username = api_username
        self.api_password = api_password
        self.passphrase = _passphrase
        self.cert_path = cert_path
        self.key_path = key_path
        self.folder_path = _load_folder_path
        self.documents_count = {}
        self.doc_id_sequence = {}
        self.max_results = _max_results
        self.config_manager = ConfigManager(_json_file_path)
        config = self.config_manager.load_config()
        self.neighbour_nodes = config['nodes']
        self.neighbour_nodes[_node_id - 1]['alive'] = True
        self.current_leader = None
        self.doc_index_metadata = doc_index_metadata
        self.db = FastJsonLoader(folder_path=self.folder_path,
                                 documents_per_file=1000,
                                 node_id=self.node_id,
                                 node_count=len(self.neighbour_nodes),
                                 doc_index_collection=doc_index_metadata)
        self.indexer = IndexCreator(self.db,
                                    db_name=db_name,
                                    index_collection=index_collection,
                                    metadata_collection=metadata_collection)
        self.engine = SearchEngine(self.indexer, max_results=10000)
        self.db.doc_id = self.node_id
        self.db.node_count = len(config['nodes'])

    def handle_request(self, request):
        """
        Handles an incoming request.

        Args:
            request (str): The JSON-encoded request.

        Returns:
            str: The JSON-encoded response to the request.
        """
        data = json.loads(request)
        action = data.get('action', '')

        if action == 'heartbeat':
            # Responds with a status of 'OK' for heartbeat action.
            return json.dumps({'status': 'OK'})
        elif action == 'load_documents':
            # Loads documents from the database.
            self.db.load_documents()
            return json.dumps({'status': 'OK'})
        elif action == 'load_index':
            # Creates or loads the index.
            self.indexer.create_load_index()
            self.engine.bm25f.update_total_docs(self.indexer.index_metadata.total_docs)
            return json.dumps({'status': 'OK'})
        elif action == 'get_data':
            # Handles a request to get data.
            # Input: data (request payload)
            # Output: results (response payload)
            results = self.handle_get_data(data)
            return json.dumps({'status': 'OK', 'results': results})
        elif action == 'update_alive':
            # Updates the alive status of a node.
            # Input: results (dictionary with node id and alive status)
            results = data.get('attr1', '')
            key = next(iter(results.keys()))
            self.neighbour_nodes[int(key) - 1]['alive'] = results[key]
            self.config_manager.save_config(self.neighbour_nodes)
            return json.dumps({'status': 'OK'})
        elif action == 'search_ids':
            # Performs a search based on IDs.
            # Input: data (request payload)
            # Output: results (response payload)
            results = self.search_ids(data)
            return json.dumps({'status': 'OK', 'results': results})
        elif action == 'set_starting_doc_id':
            # Sets the starting document ID.
            # Input: doc_id (starting document ID)
            # Output: doc_id, status
            return json.dumps({'doc_id': data.get('doc_id', ''), 'status': 'OK'})
        elif action == 'insert_docs':
            # Inserts new documents into the database.
            # Input: new_docs (documents to insert)
            self.db.insert_documents(data.get('new_docs', ''))
            return json.dumps({'status': 'OK'})
        elif action == 'get_config':
            # Retrieves the current configuration.
            # Output: config (response payload)
            return json.dumps({'status': 'OK', "config": self.neighbour_nodes})
        else:
            # Handles an unknown request.
            return json.dumps({'error': 'Unknown request'})

    # run without SSL encryption
    def run(self):
        """
        Runs the server and handles incoming requests.
        It listens for incoming connections on the specified host and port.
        When a connection is accepted, it creates a new thread to handle the request.
        The 'handle_request_wrapper' method is called to process the request.

        Returns:
            None
        """
        if self.neighbour_nodes[self.node_id - 1]['leader'] and self.neighbour_nodes[self.node_id - 1]['first_boot']:
            heartbeat_thread = threading.Thread(target=self.check_heartbeats)
            heartbeat_thread.start()
        if not self.neighbour_nodes[self.node_id - 1]['first_boot']:
            # get config from other nodes
            for _node in self.neighbour_nodes:
                if self.node_id != _node['id'] and _node['alive']:
                    try:
                        response = send_request((_node['host'], _node['port']), {
                            'action': 'get_config'
                        })
                        if response.get('status') == 'OK':
                            self.neighbour_nodes = response['config']
                            break
                    except socket.error as e:
                        logger.log_info(f"Failed to get config from node {_node['id']} with error {e}")
            # Start db and index
            self.db.load_documents()
            self.indexer.create_load_index()
            self.engine.bm25f.update_total_docs(self.indexer.index_metadata.total_docs)
            # inform other nodes for recovery
            self.neighbour_nodes[self.node_id - 1]['alive'] = True
            self.config_manager.save_config(self.neighbour_nodes)
            execute_action('update_alive', self.neighbour_nodes, self.node_id, {self.node_id: True})

        # Update first_boot to false. If server crashes when restart
        # it will perform additional actions
        self.neighbour_nodes[self.node_id - 1]['first_boot'] = False
        self.config_manager.save_config(self.neighbour_nodes)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.node_host, self.node_port))
            sock.listen(5)
            logger.log_info(f"Node {self.node_id} listening on port {self.node_port}")

            while True:
                conn, addr = sock.accept()
                logger.log_info(f"Node {self.node_id}: Connection accepted from {addr}")
                threading.Thread(target=self.handle_request_wrapper, args=(conn,)).start()

    def handle_request_wrapper(self, conn):
        """
        Wraps the handling of a request received from a client.

        Args:
            conn (socket): The connection object for the request.

        Returns:
            None
        """
        request = receive_message(conn)
        logger.log_info(f"Node {self.node_id}: Received request: {request[:100]}")
        response = self.handle_request(request)
        logger.log_info(f"Node {self.node_id}: Sending response: {response[:100]}")
        send_message(response, conn)

    def check_heartbeats(self):
        """
        Checks the heartbeats of the neighbour nodes and then send the load_document request.

        Returns:
            None
        """
        execute_action('heartbeat', self.neighbour_nodes, self.node_id)
        self.send_load_documents()

    def send_load_documents(self):
        """
        Sends load_documents commands to the leader and other nodes.

        Returns:
            None
        """
        # load documents for leader
        load_documents_thread = threading.Thread(target=self.db.load_documents)
        load_documents_thread.start()
        # send load_documents commands to all other nodes
        execute_action('load_documents', self.neighbour_nodes, self.node_id)
        load_documents_thread.join()
        self.send_create_index()

    def send_create_index(self):
        """
        Sends create_index commands to the leader and other nodes.

        Returns:
            None
        """
        # load index for leader
        create_load_index_thread = threading.Thread(target=self.indexer.create_load_index)
        create_load_index_thread.start()
        execute_action('load_index', self.neighbour_nodes, self.node_id)
        create_load_index_thread.join()
        # change total docs in bm25f for leader
        self.engine.bm25f.update_total_docs(self.indexer.index_metadata.total_docs)

    def get_shard(self, key):
        """
        Returns the shard for a given key.

        Args:
            key (str): The key for which shard is to be determined.

        Returns:
            dict: The shard node.
        """
        num_shards = len(self.neighbour_nodes)
        shard_id = int(sha256(key.encode()).hexdigest(), 16) % num_shards
        return self.neighbour_nodes[shard_id]

    def update_config(self, _config_file):
        """
        Updates the local configuration file with the current neighbour node information.

        Args:
            _config_file (str): The path to the configuration file.

        Returns:
            None
        """
        with open(_config_file, 'w') as f:
            config = json.load(f)
            config['nodes'] = self.neighbour_nodes
            json.dump(config, f, indent=4)

    def handle_get_data(self, data):
        """
        Handles the 'get_data' action and forwards the request
        to the appropriate nodes.

        Args:
            data (dict): The request data.

        Returns:
            list: The response with the requested data.
        """
        ids = data.get('ids', '')
        if not data.get('forwarded'):
            results_dict = {}
            ids_per_node = split_ids(ids, self.db.node_count)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for _node, value in ids_per_node.items():
                    if isinstance(_node, dict):
                        _node = _node['id']
                    if not self.neighbour_nodes[_node - 1]['alive']:
                        continue

                    if _node == self.node_id:
                        futures.append(executor.submit(self.thread_safe_get_data, _node, value, results_dict))
                    else:
                        futures.append(executor.submit(self.thread_safe_get_data_request, _node, value, results_dict))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.log_error(f"An error occurred: {e}")

            results = []
            for _node in sorted(results_dict.keys()):
                results.extend(results_dict[_node])
            return results
        else:
            return json.dumps({'results': self.db.get_data(ids)})

    def thread_safe_get_data(self, _node, value, results_dict):
        get_data_results = self.db.get_data(value)
        with self.results_lock:
            results_dict[_node] = get_data_results

    def thread_safe_get_data_request(self, _node, value, results_dict):
        """
            Sends a thread-safe get data request to a specified node.

            Args:
                _node (int): The index of the node to send the request to.
                value (int): The value to send with the request.
                results_dict (dict): A dictionary to store the results.

            Raises:
                socket.error: If there is an error with the socket connection.

            Returns:
                None
        """
        try:
            response = send_request(
                (self.neighbour_nodes[_node - 1]['host'], self.neighbour_nodes[_node - 1]['port']), {
                    'action': 'get_data', 'forwarded': True, 'ids': value
                })
            response_results = json.loads(response.get('results'))['results']
            with self.results_lock:
                results_dict[_node] = response_results
        except socket.error:
            self.neighbour_nodes[_node - 1]['alive'] = False
            self.config_manager.save_config(self.neighbour_nodes)
            execute_action('update_alive', self.neighbour_nodes, self.node_id, {str(_node): False})
            api_requester = APIRequester(self.api_url, self.api_username, self.api_password)
            api_response = api_requester.post_update_config_endpoint(self.neighbour_nodes)
            logger.log_error(f'Update api config response: {api_response}')

    def search_ids(self, data):
        """
        Searches for IDs based on the given query. It forwards the
        request to all other nodes.

        Args:
            data (dict): The request data containing the query to be searched.
                         It should be a dictionary with the following key:
                         - 'query': The query string to search for IDs.

        Returns:
            list: The response with the searched IDs.
                  It returns a list of IDs matching the query.
        """
        query = data.get('query', '')
        if not data.get('forwarded'):
            results = defaultdict(float)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for _node in self.neighbour_nodes:
                    if not _node['alive']:
                        continue

                    if _node['id'] == self.node_id:
                        futures.append(executor.submit(self.thread_safe_search_ids, query, results))
                    else:
                        futures.append(executor.submit(self.thread_safe_search_ids_request, _node['id'],
                                                       query, results))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.log_error(f"An error occurred: {e}")

            return list(map(int, heapq.nlargest(self.max_results, results.keys(), key=results.get)))
        else:
            return json.dumps({'results': self.engine.search(query)})

    def thread_safe_search_ids(self, query, results):
        search_results = self.engine.search(query)
        with self.results_lock:
            results.update(search_results)

    def thread_safe_search_ids_request(self, _node, query, results):
        """
            Sends a thread-safe search IDs request to a specified node.

            Args:
                _node (int): The node to send the request to.
                query (str): The query string.
                results (dict): A dictionary to store the results.

            Raises:
                socket.error: If there is an error with the socket connection.

            Returns:
                None
        """
        try:
            response = send_request(
                (self.neighbour_nodes[_node - 1]['host'], self.neighbour_nodes[_node - 1]['port']), {
                    'action': 'search_ids', 'forwarded': True, 'query': query
                })
            response_results = json.loads(response.get('results'))['results']
            with self.results_lock:
                results.update(response_results)
        except socket.error:
            self.neighbour_nodes[_node - 1]['alive'] = False
            self.config_manager.save_config(self.neighbour_nodes)
            execute_action('update_alive', self.neighbour_nodes, self.node_id, {str(_node): False})
            api_requester = APIRequester(self.api_url, self.api_username, self.api_password)
            api_response = api_requester.post_update_config_endpoint(self.neighbour_nodes)
            logger.log_error(f'Update api config response: {api_response}')


if __name__ == '__main__':
    sys.path.insert(0, '../indexer/')
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_config", help="Path to the config.json file", required=True)
    parser.add_argument("--ini_config", help="Path to the config.ini file", required=True)
    parser.add_argument("--node_id", type=int, help="ID of the node", required=True)
    args = parser.parse_args()

    ini_config = IniConfig(args.ini_config)
    json_config = JsonConfig(args.json_config)
    nodes = json_config.get_property('nodes')[args.node_id - 1]

    d_node = DistributedNode(_node_id=args.node_id,
                             _node_host=nodes['host'],
                             _node_port=nodes['port'],
                             _json_file_path=args.json_config,
                             _load_folder_path=ini_config.get_property('NodeSettings', 'load_folder_path'),
                             _max_results=int(ini_config.get_property('FastJsonLoader', 'max_results')),
                             db_name=ini_config.get_property('Database', 'db_name'),
                             index_collection=ini_config.get_property('Database', 'index_collection'),
                             metadata_collection=ini_config.get_property('Database', 'metadata_collection'),
                             doc_index_metadata=ini_config.get_property('Database', 'doc_index_metadata'),
                             cert_path=ini_config.get_property('SSL', 'cert_path'),
                             key_path=ini_config.get_property('SSL', 'key_path'),
                             _passphrase=ini_config.get_property('SSL', 'passphrase'),
                             api_url=ini_config.get_property('API', 'url'),
                             api_username=ini_config.get_property('API', 'username'),
                             api_password=ini_config.get_property('API', 'password'))
    d_node.run()
