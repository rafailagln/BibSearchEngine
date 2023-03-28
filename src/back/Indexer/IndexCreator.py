from ErrorHandling.Exceptions import NoMetadataException
from Indexer.IndexMetadata import Metadata
from Preprocessor.DataCleaner import DataCleaner
from Basics.connection2 import MongoDBConnection
import logging

from Indexer.Trie import TrieIndex

TITLE = 0
ABSTRACT = 1

cleaner = DataCleaner()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class IndexCreator:
    def __init__(self, db, db_name='M151', index_collection='Index', metadata='Metadata'):
        self.db_name = db_name
        self.metadata_db = metadata
        self.index_collection = index_collection
        self.index_dictionary = TrieIndex()
        self.db = db
        self.index_metadata = Metadata()

    def create_index(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_db)
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            docs = self.db.get_all_documents()
            if index_collection.count_documents({}) == 0:
                # Index collection is empty, create index and save to collection
                logging.info("Creating index...")
                est_total_size = self.db.doc_id - 1
                count = 0
                progress_threshold = 5000
                for doc in docs:
                    self.index_metadata.update_doc_num()
                    doc_id = doc['doc_id']
                    if doc['title'] != ' ':
                        cleaned_words = cleaner.cleanData(doc['title'])
                        self.node_adder(doc_id, cleaned_words, TITLE)
                        count += 1
                        self.index_metadata.add_doc_length_field(doc_id, len(cleaned_words), field=TITLE)
                        self.index_metadata.increase_average_length(len(cleaned_words), field=TITLE)
                    if doc['abstract'] != ' ':
                        cleaned_words = cleaner.cleanData(doc['abstract'])
                        self.node_adder(doc_id, cleaned_words, ABSTRACT)
                        count += 1
                        self.index_metadata.add_doc_length_field(doc_id, len(cleaned_words), field=ABSTRACT)
                        self.index_metadata.increase_average_length(len(cleaned_words), field=ABSTRACT)
                    if count % progress_threshold == 0:
                        print(f'Created {count}/{est_total_size} docs ({count / est_total_size:.2%})')
                logging.info("Created index.\n")
                self.index_metadata.calculate_average_length()
                # Save index to db
                # logging.info("Saving index to db...")
                # self.index_dictionary.save(index_collection)
            else:
                # Metadata collection must exist in MondoDB
                if metadata_collection.count_documents({}) == 0:
                    raise NoMetadataException()
                # Index exists, load index from db
                logging.info("Loading index...")
                self.index_dictionary.load(index_collection)
                self.index_metadata.load(metadata_collection)

    def node_adder(self, _id, cleaned_words, _type):
        _counter = 1
        for word in cleaned_words:
            self.index_dictionary.insert(word, (_id, _counter, _type))
            _counter += 1
