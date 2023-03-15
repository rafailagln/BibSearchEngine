from Preprocessor.DataCleaner import DataCleaner
from Basics.connection2 import MongoDBConnection
from Indexer.IndexValueInfo import InfoClass
import json
import logging

TITLE = 0
ABSTRACT = 1

cleaner = DataCleaner()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def node_adder(_id, _value, _counter, _index_dictionary, type):
    cleaned_words = cleaner.cleanData(_value)
    for word in cleaned_words:
        _listNode = InfoClass(type, _counter, _id)
        if word in _index_dictionary:
            _index_dictionary[word].append(_listNode)
        else:
            _index_dictionary[word] = [_listNode]
        _counter += 1
    return _counter, _index_dictionary


class IndexCreator:
    def __init__(self, db_name='M151', index_collection='Index', data_collection='Papers'):
        self.db_name = db_name
        self.index_collection = index_collection
        self.data_collection = data_collection
        self.index_dictionary = {}

    def create_index(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            data_collection = mongo.get_database(self.db_name).get_collection(self.data_collection)
            if index_collection.count_documents({}) == 0:
                # Index collection is empty, create index and save to collection
                logging.info("Creating index...")
                data = data_collection.find({}, {"_id": 1, "title": 1, "abstract": 1})
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
                logging.info("Created index.\n")
                # Save index to db
                logging.info("Saving index to db...")
                self._save_dict_to_mongo(index_collection)
            else:
                # Index exists, load index from db
                logging.info("Loading index...")
                self._load_dict_from_mongo(index_collection)

    # make batch_size bigger if index is big
    def _save_dict_to_mongo(self, collection, batch_size=2000):
        total_docs = len(self.index_dictionary)
        current_doc = 0
        batch = []
        for key, values in self.index_dictionary.items():
            doc = {
                '_id': key,
                'info': [v.__json__() for v in values]
            }
            batch.append(doc)
            current_doc += 1
            if current_doc % batch_size == 0 or current_doc == total_docs:
                collection.insert_many(batch)
                batch = []
                progress_pct = (current_doc / total_docs) * 100
                logging.info(f"Progress: {progress_pct:.2f}%")

    def _load_dict_from_mongo(self, collection):
        total_docs = collection.count_documents({})
        current_doc = 0
        documents = collection.find()
        for doc in documents:
            key = doc['_id']
            info_list = []
            for info in doc['info']:
                info_obj = InfoClass(info['type'], info['position'], info['docid'])
                info_list.append(info_obj)
            self.index_dictionary[key] = info_list
            current_doc += 1
            progress_pct = (current_doc / total_docs) * 100
            logging.info(f"Progress: {progress_pct:.2f}%")
