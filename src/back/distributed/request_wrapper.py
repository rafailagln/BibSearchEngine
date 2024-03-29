import json
import socket

from distributed.utils import send_request
from logger import MyLogger

logger = MyLogger()


class RequestWrapper:
    def __init__(self, config_file):
        """
        Initializes a RequestWrapper object.

        Args:
            config_file (str): The path to the JSON configuration file.

        Returns:
            None
        """
        self._config_file = config_file
        self._index = -1
        self._load_config()

    def _load_config(self):
        """
        Loads the configuration from the JSON file.

        Args:
            None

        Returns:
            None
        """
        with open(self._config_file, 'r') as file:
            self._config = json.load(file)
        self.neighbour_nodes = self._config['nodes']

    def _get_next_node(self):
        """
        Returns the next neighbor node in a round-robin fashion.

        Args:
            None

        Returns:
            next_node (dict): The next neighbor node.
        """
        self._index = (self._index + 1) % len(self.neighbour_nodes)
        return self.neighbour_nodes[self._index - 1]

    def search_ids(self, query):
        """
        Sends a search request to one of the neighbor nodes to search the
        neighbor node for its ids.

        Args:
            query (str): The search query.

        Returns:
            response (dict): The response from the neighbor node, or None if an
            error occurred.
        """
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
                    logger.logger(f"Failed to send search_ids request to {sending_node}: {e}")
            i += 1

    def fetch_data(self, ids):
        """
        Sends a fetch data request to one of the neighbor nodes.

        Args:
            ids (list): The list of IDs to fetch data for.

        Returns:
            response (dict): The response from the neighbor node with the
            data of sent ids, or None if an error occurred.
        """
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
                    logger.log_error(f"Failed to send get_data request to {sending_node}: {e}")
            i += 1
