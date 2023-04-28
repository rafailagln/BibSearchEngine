from Indexer.IndexMetadata import Metadata
from Indexer.Trie import TrieIndex
from Preprocessor.DataCleaner import DataCleaner
from Basics.connection import MongoDBConnection
import logging

TITLE = 0
ABSTRACT = 1

cleaner = DataCleaner()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class IndexCreator:
    def __init__(self, db, metadata_collection, db_name='M151Dev', index_collection='Index',):
        self.db_name = db_name
        self.index_collection = index_collection
        self.index_dictionary = TrieIndex(db_name=db_name, index_collection=index_collection)
        self.db = db
        self.index_metadata = Metadata(metadata_collection=metadata_collection)

    def create_load_index(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            index_collection = mongo.get_database(self.db_name).get_collection(self.index_collection)
            docs = self.db.get_all_documents()
            self.index_metadata.set_total_docs(len(docs))
            if index_collection.count_documents({}) == 0:
                # Index collection is empty, create index and save to collection
                logging.info("Creating index...")
                est_total_size = self.db.doc_id - 1
                count = 0
                progress_threshold = 5000
                for doc in docs:
                    doc_id = doc['doc_id']
                    if doc['title'] != ' ':
                        cleaned_words = cleaner.cleanData(doc['title'])
                        self.node_adder(doc_id, cleaned_words, TITLE)
                        self.index_metadata.add_doc_length_field(doc_id, len(cleaned_words), field=TITLE)
                        self.index_metadata.increase_average_length(len(cleaned_words), field=TITLE)
                    if doc['abstract'] != ' ':
                        cleaned_words = cleaner.cleanData(doc['abstract'])
                        self.node_adder(doc_id, cleaned_words, ABSTRACT)
                        self.index_metadata.add_doc_length_field(doc_id, len(cleaned_words), field=ABSTRACT)
                        self.index_metadata.increase_average_length(len(cleaned_words), field=ABSTRACT)
                    if doc['referenced_by'] != ' ':
                        self.index_metadata.add_referenced_by(doc_id, doc['referenced_by'])
                    count += 1
                    if count % progress_threshold == 0:
                        print(f'Created {count}/{est_total_size} docs ({count / est_total_size:.2%})', end="\r", flush=True)
                logging.info("Created index.")
                self.index_metadata.calculate_average_length()
                self.index_metadata.normalize_referenced_by()
                logging.info("Saving index to db...")
                self.index_dictionary.save()
                logging.info("Saving metadata to db...")
                self.index_metadata.save()
            else:
                logging.info("Loading index...")
                self.index_dictionary.load()
                logging.info("Loading metadata...")
                self.index_metadata.load()

    def node_adder(self, _id, cleaned_words, _type):
        _counter = 1
        for word in cleaned_words:
            self.index_dictionary.insert(word, (_id, _counter, _type))
            _counter += 1
