from distributed.node import DistributedNode

if __name__ == '__main__':
    node1 = DistributedNode(_node_id=1, _node_port=9091, _config_file='../node_data/node1/load/config.json',
                            _folder_path='../node_data/node1/load',
                            _max_results=10000, db_name='M151Dev', index_collection='IndexNode1',
                            metadata_collection='MetadataNode1')
    node1.run()
