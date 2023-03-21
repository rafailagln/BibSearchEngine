class TrieNode:
    def __init__(self):
        self.children = {}
        self.values = []


class TrieIndex:
    def __init__(self):
        self.root = TrieNode()
        self.key_count = 0

    def insert(self, key, value):
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.values.append(value)
        self.key_count += 1

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

    def save(self, collection, batch_size=2000):
        total_documents = self.key_count

        # Delete existing documents in the collection
        collection.delete_many({})

        # Create a batch of documents to insert
        batch = []
        count = 0
        progress_threshold = 5000
        for key in self.get_keys():
            values = self.search(key)
            doc = {'_id': key, 'values': values}
            batch.append(doc)
            count += 1
            if count % batch_size == 0:
                collection.insert_many(batch)
                batch = []
            if count % progress_threshold == 0:
                print(f"Processed {count} documents... {count / total_documents:.2%} ({count}/{total_documents})")
        if batch:
            collection.insert_many(batch)
        print("Finished saving trie to MongoDB")

    def load(self, collection):
        total_documents = collection.estimated_document_count()
        cursor = collection.find()
        count = 0
        progress_threshold = 5000
        for doc in cursor:
            key = doc['_id']
            values = doc['values']
            for value in values:
                self.insert(key, value)
            count += 1
            if count % progress_threshold == 0:
                print(f"Processed {count} documents... {count / total_documents:.2%} ({count}/{total_documents})")
        print(f"Loaded {total_documents} documents from collection")
        return self




