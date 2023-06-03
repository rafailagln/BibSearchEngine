import sys
from distributed.node import DistributedNode
from configurations.read_config import IniConfig, JsonConfig


def create_distributed_node(ini_config_path, json_config_path, node_id):
    """
    Creates a DistributedNode object with the provided configuration files and node ID.
    This function initializes a DistributedNode object based on the configuration files and node ID. It reads the
    configuration details from the INI and JSON files, extracts the specific node configuration based on the given
    node ID, and sets up the DistributedNode object with the extracted parameters.

    Inputs:
    - ini_config_path: The path to the INI configuration file.
    - json_config_path: The path to the JSON configuration file.
    - node_id: The ID of the node.

    Output:
    - Returns the created DistributedNode object.
    """

    sys.path.insert(0, '../indexer/')

    ini_config = IniConfig(ini_config_path)
    json_config = JsonConfig(json_config_path)
    nodes = json_config.get_property('nodes')[node_id - 1]

    node = DistributedNode(_node_id=node_id,
                           _node_host=nodes['host'],
                           _node_port=nodes['port'],
                           _json_file_path=json_config_path,
                           _load_folder_path=ini_config.get_property('NodeSettings', 'load_folder_path'),
                           _max_results=int(ini_config.get_property('FastJsonLoader', 'max_results')),
                           db_name=ini_config.get_property('Database', 'db_name'),
                           index_collection=ini_config.get_property('Database', 'index_collection'),
                           metadata_collection=ini_config.get_property('Database', 'metadata_collection'),
                           cert_path=ini_config.get_property('SSL', 'cert_path'),
                           key_path=ini_config.get_property('SSL', 'key_path'),
                           _passphrase=ini_config.get_property('SSL', 'passphrase'),
                           api_url=ini_config.get_property('API', 'url'),
                           api_username=ini_config.get_property('API', 'username'),
                           api_password=ini_config.get_property('API', 'password'))
    return node
