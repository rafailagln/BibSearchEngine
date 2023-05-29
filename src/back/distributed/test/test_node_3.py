from distributed.node import DistributedNode

if __name__ == '__main__':
    node3 = DistributedNode(_node_id=3, _node_port=9093, _config_file='../node_data/node3/load/config.json',
                            _folder_path='../node_data/node3/load',
                            _max_results=10000, db_name='M151Dev', index_collection='IndexNode3',
                            metadata_collection='MetadataNode3')
    node3.run()
