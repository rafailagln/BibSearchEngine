from collections import defaultdict
from Basics.connection import MongoDBConnection


class Metadata:

    def __init__(self, db_name='M151Dev', metadata_collection='Metadata'):
        self.length_field = defaultdict(lambda: defaultdict(int))
        self.average_length = defaultdict(float)
        self.total_docs = 0
        self.db_name = db_name
        self.metadata_collection = metadata_collection

    def update_doc_num(self):
        self.total_docs += 1

    def add_doc_length_field(self, doc_id, length, field):
        self.length_field[str(doc_id)][str(field)] = length

    def increase_average_length(self, length, field):
        self.average_length[str(field)] += length

    def calculate_average_length(self):
        for field in self.average_length.keys():
            self.average_length[field] /= self.total_docs

    def load(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_collection)
            metadata_document = metadata_collection.find_one({"metadata": "metadata"})
            if metadata_document:
                length_field_data = metadata_document.get("length_field", {})
                for doc_id, fields in length_field_data.items():
                    self.length_field[doc_id] = fields
                self.average_length = defaultdict(float, metadata_document.get("average_length", {}))
                self.total_docs = metadata_document.get("total_docs", 0)
            else:
                print("No metadata found in the collection. Starting with default values.")

    # TODO:
    #  1. Don't save metadata, total_docs  attribute
    #  2. Insert one document for average_length_data
    #  3. Insert one document per entry of length field
    def save(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_collection)

            metadata_document = {
                "metadata": "metadata",
                "length_field": self.length_field,
                "average_length": self.average_length,
                "total_docs": self.total_docs
            }

            metadata_collection.update_one({"metadata": "metadata"}, {"$set": metadata_document}, upsert=True)
