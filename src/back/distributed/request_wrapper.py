import json
import socket

from distributed.utils import send_request


class RequestWrapper:
    def __init__(self, config_file):
        self._config_file = config_file
        self._index = -1
        self._load_config()

    def _load_config(self):
        with open(self._config_file, 'r') as file:
            self._config = json.load(file)
        self.neighbour_nodes = self._config['nodes']

    def _get_next_node(self):
        self._index = (self._index + 1) % len(self.neighbour_nodes)
        return self.neighbour_nodes[self._index - 1]

    def search_ids(self, query):
        i = 1
        while i <= 10:
            next_node = self._get_next_node()
            if next_node['alive']:
                sending_node = (next_node['host'], next_node['port'])
                request = {'action': 'search_ids', 'forwarded': False, 'query': query}
                try:
                    response = send_request(sending_node, request)
                    if response is not None:
                        return response
                except socket.error as e:
                    print(e)
            i += 1

    def fetch_data(self, ids):
        i = 1
        while i <= 10:
            next_node = self._get_next_node()
            if next_node['alive']:
                sending_node = (next_node['host'], next_node['port'])
                request = {'action': 'get_data', 'forwarded': False, 'ids': ids}
                try:
                    response = send_request(sending_node, request)
                    if response is not None:
                        return response
                except socket.error as e:
                    print(e)
            i += 1
