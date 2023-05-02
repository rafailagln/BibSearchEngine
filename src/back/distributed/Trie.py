from Basics.connection import MongoDBConnection


class TrieNode:
    def __init__(self):
        self.children = {}
        self.values = []


class TrieIndex:
    def __init__(self, db_name='M151Dev', index_collection='Index'):
        self.root = TrieNode()
        self.db_name = db_name
        self.index_collection = index_collection

    def insert_batch(self, docs):
        for doc in docs:
            self.insert(doc[0], doc[1])

    def insert(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.values.append(value)

    def search_batch(self, keys):
        results = {}
        for key in keys:
            results[key] = self.search(key)
        return results

    def search(self, key):
        node = self.root
        for char in key:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.values

    def delete_batch(self, key_values):
        for key, value in key_values.items():
            self.delete(key, value)

    def delete(self, key, value=None):
        def _delete(node, _key, depth):
            if depth == len(_key):
                if value is None:
                    node.values = []
                else:
                    if value in node.values:
                        node.values.remove(value)
                if not node.children and not node.values:
                    return None
                return node
            char = _key[depth]
            if char in node.children:
                node.children[char] = _delete(node.children[char], _key, depth + 1)
                if not node.children[char]:
                    del node.children[char]
                if not node.children and not node.values:
                    return None
            return node

        self.root = _delete(self.root, key, 0)

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
            # progress_threshold = 5000
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
            print(f"Loaded {total_documents} documents from collection")
            return self

    def is_empty(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            if index_collection.count_documents({}) == 0:
                return True
            else:
                return False
