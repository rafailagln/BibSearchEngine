from node_helper import create_distributed_node

if __name__ == '__main__':
    ini_config_path = '../node_data/node2/load/config.ini'
    json_config_path = '../node_data/node2/load/config.json'
    node_id = 2

    node1 = create_distributed_node(ini_config_path, json_config_path, node_id)
    node1.run()
