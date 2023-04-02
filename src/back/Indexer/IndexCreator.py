from Preprocessor.DataCleaner import DataCleaner
from Basics.connection2 import MongoDBConnection
import logging

from Indexer.Trie import TrieIndex

TITLE = 0
ABSTRACT = 1

cleaner = DataCleaner()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class IndexCreator:
    def __init__(self, db, db_name='M151', index_collection='Index'):
        self.db_name = db_name
        self.index_collection = index_collection
        self.index_dictionary = TrieIndex()
        self.db = db

    def create_index(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            docs = self.db.get_all_documents()
            if index_collection.count_documents({}) == 0:
                # Index collection is empty, create index and save to collection
                logging.info("Creating index...")
                est_total_size = self.db.doc_id - 1
                count = 0
                progress_threshold = 5000
                for doc in docs:
                    doc_id = doc['doc_id']
                    if doc['title'] != ' ':
                        self.node_adder(doc_id, doc['title'], TITLE)
                    if doc['abstract'] != ' ':
                        self.node_adder(doc_id, doc['abstract'], ABSTRACT)
                    count += 1
                    if count % progress_threshold == 0:
                        print(f'Created {count}/{est_total_size} docs ({count / est_total_size:.2%})', end="\r", flush=True)
                logging.info("Created index.")
                # Save index to db
                logging.info("Saving index to db...")
                self.index_dictionary.save(index_collection)
            else:
                # Index exists, load index from db
                logging.info("Loading index...")
                self.index_dictionary.load(index_collection)

    def node_adder(self, _id, _value, _type):
        _counter = 1
        cleaned_words = cleaner.cleanData(_value)
        for word in cleaned_words:
            self.index_dictionary.insert(word, (_id, _counter, _type))
            _counter += 1
