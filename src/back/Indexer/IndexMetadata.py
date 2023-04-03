from collections import defaultdict
from Basics.connection2 import MongoDBConnection


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
        self.length_field[doc_id][field] = length

    def increase_average_length(self, length, field):
        self.average_length[field] += length

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
                    self.length_field[int(doc_id)] = defaultdict(int, fields)
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
            length_field_data = dict()
            for doc_id, fields in self.length_field.items():
                length_field_data[str(doc_id)] = {'0': fields[0], '1': fields[1]}

            average_length_data = dict()
            average_length_data['0'] = self.average_length[0]
            average_length_data['1'] = self.average_length[1]

            metadata_document = {
                "metadata": "metadata",
                "length_field": length_field_data,
                "average_length": average_length_data,
                "total_docs": self.total_docs
            }
            metadata_collection.update_one({"metadata": "metadata"}, {"$set": metadata_document}, upsert=True)
