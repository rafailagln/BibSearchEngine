from node3 import DistributedNode

if __name__ == '__main__':
    node2 = DistributedNode(_node_id=2, _node_port=9092, _config_file='config.json',
                            _folder_path='/path/to/node2/load/',
                            _max_results=10000, db_name='M151Dev', index_collection='IndexNode2',
                            metadata_collection='MetadataNode2')
    node2.run()
