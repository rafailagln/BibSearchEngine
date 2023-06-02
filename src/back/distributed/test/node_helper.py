import sys
from distributed.node import DistributedNode
from configurations.ini_config import IniConfig
from configurations.json_config import JsonConfig

def create_distributed_node(ini_config_path, json_config_path, node_id):
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
