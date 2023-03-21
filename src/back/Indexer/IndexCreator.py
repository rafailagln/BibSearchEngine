from Preprocessor.DataCleaner import DataCleaner
from Basics.connection2 import MongoDBConnection
import logging

from Indexer.Trie import TrieIndex

TITLE = 0
ABSTRACT = 1

cleaner = DataCleaner()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def node_adder(_id, _value, _counter, _index_dictionary, _type):
    cleaned_words = cleaner.cleanData(_value)
    for word in cleaned_words:
        _index_dictionary.insert(word, (_id, _counter, _type))
        _counter += 1
    return _counter, _index_dictionary


class IndexCreator:
    def __init__(self, db_name='M151', index_collection='Index', data_collection='Papers'):
        self.db_name = db_name
        self.index_collection = index_collection
        self.data_collection = data_collection
        self.index_dictionary = TrieIndex()

    def create_index(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            data_collection = mongo.get_database(self.db_name).get_collection(self.data_collection)
            if index_collection.count_documents({}) == 0:
                # Index collection is empty, create index and save to collection
                logging.info("Creating index...")
                data = data_collection.find({}, {"_id": 1, "title": 1, "abstract": 1})
                est_total_size = data_collection.estimated_document_count()
                count = 0
                progress_threshold = 5000
                for doc in data:
                    doc_id = doc["_id"]
                    for field, value in doc.items():
                        counter = 1
                        if field == "title":
                            counter, self.index_dictionary = node_adder(doc_id, value[0], counter,
                                                                        self.index_dictionary,
                                                                        TITLE)
                        elif field == "abstract":
                            counter, self.index_dictionary = node_adder(doc_id, value, counter, self.index_dictionary,
                                                                        ABSTRACT)
                    count += 1
                    if count % progress_threshold == 0:
                        print(f'Created {count}/{est_total_size} docs ({count / est_total_size:.2%})')
                logging.info("Created index.\n")
                # Save index to db
                logging.info("Saving index to db...")
                self.index_dictionary.save(index_collection)
            else:
                # Index exists, load index from db
                logging.info("Loading index...")
                self.index_dictionary.load(index_collection)
