import logging
from Basics.connection import MongoDBConnection

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TrieNode:
    def __init__(self):
        self.children = {}
        self.values = []


class TrieIndex:
    def __init__(self, db_name='M151Dev', index_collection='Index'):
        self.root = TrieNode()
        self.db_name = db_name
        self.index_collection = index_collection

    def insert(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.values.append(value)

    def search(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.values

    def get_keys(self):
        keys = []

        def traverse(node, prefix):
            if node.values:
                keys.append(prefix)
            for char, child_node in node.children.items():
                traverse(child_node, prefix + char)

        traverse(self.root, "")
        return keys

    def save(self, batch_size=2000):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            total_keys = self.get_keys()
            total_documents = len(total_keys)

            # Delete existing documents in the collection
            index_collection.delete_many({})

            # Create a batch of documents to insert
            batch = []
            count = 0
            progress_threshold = 5000
            for key in total_keys:
                values = self.search(key)
                doc = {'_id': key, 'values': values}
                batch.append(doc)
                count += 1
                if count % batch_size == 0:
                    index_collection.insert_many(batch)
                    batch = []
                # if count % progress_threshold == 0:
                print(f"Processed {count} documents... {count / total_documents:.2%} ({count}/{total_documents})",
                      end="\r", flush=True)
            if batch:
                index_collection.insert_many(batch)
                print(f"Processed {count} documents... {count / total_documents:.2%} ({count}/{total_documents})",
                      end="\r", flush=True)
            print("Finished saving trie to MongoDB")

    def load(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            total_documents = index_collection.estimated_document_count()
            cursor = index_collection.find()
            count = 0
            progress_threshold = 5000
            for doc in cursor:
                key = doc['_id']
                values = doc['values']
                for value in values:
                    self.insert(key, value)
                count += 1
                if count % progress_threshold == 0:
                    print(f"Processed {count} documents... {count / total_documents:.2%} ({count}/{total_documents})",
                          end="\r", flush=True)
            logging.info(f"Loaded {total_documents} documents from collection")
            return self
