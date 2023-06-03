from db.connection import MongoDBConnection


class TrieNode:
    def __init__(self):
        """
        Initializes a TrieNode object.

        Args:
            None

        Returns:
            None
        """
        self.children = {}
        self.values = []


class TrieIndex:
    def __init__(self, db_name='M151', index_collection='Index'):
        """
        Initializes a TrieIndex object.

        Args:
            db_name (str): The name of the MongoDB database to connect to (default: 'M151').
            index_collection (str): The name of the collection to store the index in MongoDB
                                   (default: 'Index').

        Returns:
            None
        """
        self.root = TrieNode()
        self.db_name = db_name
        self.index_collection = index_collection

    def insert_batch(self, docs):
        """
        Inserts a batch of documents into the trie index.

        Args:
            docs (list): A list of tuples (key, value) representing the documents to be inserted.

        Returns:
            None
        """
        for doc in docs:
            self.insert(doc[0], doc[1])

    def insert(self, key, value):
        """
        Inserts a key-value pair into the trie index.

        Args:
            key (str): The key to be inserted.
            value: The value associated with the key.

        Returns:
            None
        """
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.values.append(value)

    def search_batch(self, keys):
        """
        Searches for multiple keys in the trie index and returns the corresponding values.

        Args:
            keys (list): A list of keys to be searched.

        Returns:
            results (dict): A dictionary where keys are the input keys and values are the search results
                            (list of values).
        """
        results = {}
        for key in keys:
            results[key] = self.search(key)
        return results

    def search(self, key):
        """
        Searches for a key in the trie index and returns the corresponding values.

        Args:
            key (str): The key to be searched.

        Returns:
            values (list): A list of values associated with the key.
        """
        node = self.root
        for char in key:
            if char not in node.children:
                return []
            node = node.children[char]
        return node.values

    def delete_batch(self, key_values):
        """
        Deletes multiple key-value pairs from the trie index.

        Args:
            key_values (dict): A dictionary where keys are the keys to be deleted and values are the corresponding
                               values.

        Returns:
            None
        """
        for key, value in key_values.items():
            self.delete(key, value)

    def delete(self, key, value=None):
        """
        Deletes a key-value pair from the trie index. If value is None, all values associated with the key will be
        deleted.

        Args:
            key (str): The key to be deleted.
            value: The value to be deleted (if None, all values associated with the key will be deleted).

        Returns:
            None
        """
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
        """
        Retrieves all keys stored in the trie index.

        Args:
            None

        Returns:
            keys (list): A list of keys in the trie index.
        """
        keys = []

        def traverse(node, prefix):
            if node.values:
                keys.append(prefix)
            for char, child_node in node.children.items():
                traverse(child_node, prefix + char)

        traverse(self.root, "")
        return keys

    def save(self, batch_size=2000):
        """
        Saves the trie index to MongoDB in batches for better performance.

        Args:
            batch_size (int): The number of documents to insert in each batch (default: 5000).

        Returns:
            None
        """
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
        """
        Loads the trie index from MongoDB and stores it as a TrieIndex (trie) in memory.

        Args:
            None

        Returns:
            self (TrieIndex): The loaded TrieIndex object.
        """
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
        """
        Checks if the trie index is empty.

        Args:
            None

        Returns:
            empty (bool): True if the trie index is empty, False otherwise.
        """
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            if index_collection.count_documents({}) == 0:
                return True
            else:
                return False
