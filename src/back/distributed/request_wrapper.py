import json

from distributed.utils import send_request

_config_file = './distributed/config.json'

with open(_config_file, 'r') as f:
    config = json.load(f)

nodes = config['nodes']
index = -1


def get_next_node(_index):
    return (_index + 1) % len(nodes)


def search_ids_wrapper(query):
    global index, nodes
    index = get_next_node(index)
    sending_node = (nodes[index]['host'], nodes[index]['port'])
    insert_request = {'action': 'search_ids', 'forwarded': False, 'query': query}
    return send_request(sending_node, insert_request)['results']


def fetch_data_wrapper(ids):
    global index, nodes
    index = get_next_node(index)
    sending_node = (nodes[index]['host'], nodes[index]['port'])
    insert_request = {'action': 'get_data', 'forwarded': False, 'ids': ids}
    return send_request(sending_node, insert_request)
