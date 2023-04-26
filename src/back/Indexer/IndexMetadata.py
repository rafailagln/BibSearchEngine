from collections import defaultdict
from Basics.connection import MongoDBConnection


class Metadata:

    def __init__(self, db_name='M151', metadata_collection='Metadata'):
        self.length_field = defaultdict(lambda: defaultdict(int))
        self.average_length = defaultdict(float)
        self.referenced_by = defaultdict(int)
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

    def add_referenced_by(self, doc_id, referenced):
        self.referenced_by[str(doc_id)] = referenced

    def set_total_docs(self, num):
        self.total_docs = num

    def load(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_collection)

            # Load length_field data from separate documents
            length_field_documents = metadata_collection.find({"doc_id": {"$exists": True}})
            for document in length_field_documents:
                doc_id = document["doc_id"]
                fields = document["fields"]
                self.length_field[doc_id] = fields
            print("Loaded length field metadata")

            # Load average_length data from the separate document
            average_length_document = metadata_collection.find_one({"average_length": {"$exists": True}})
            if average_length_document:
                self.average_length = defaultdict(float, average_length_document.get("average_length", {}))
            print("Loaded average length metadata")

            # Load referenced_by data from the separate document
            referenced_by_document = metadata_collection.find_one({"referenced_by": {"$exists": True}})
            if referenced_by_document:
                self.referenced_by = defaultdict(int, referenced_by_document.get("referenced_by", {}))
            print("Loaded referenced_by metadata")

            # If neither document exists, print a message and start with default values
            if length_field_documents and not average_length_document:
                print("No metadata found in the collection. Starting with default values.")

            print("Loaded all metadata from MongoDB")

    def save(self):
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_collection)

            # Save each value in length_field as a separate documents
            length_field_documents = []
            for doc_id, fields in self.length_field.items():
                length_field_documents.append({
                    "doc_id": doc_id,
                    "fields": fields
                })
            metadata_collection.insert_many(length_field_documents)
            print("Saved length field documents")

            # Save average_length data in a separate document
            average_length_document = {
                "average_length": self.average_length
            }
            metadata_collection.update_one({"average_length": {"$exists": True}}, {"$set": average_length_document},
                                           upsert=True)
            print("Saved average length document")

            # Save referenced_by data in a separate document
            referenced_by_document = {
                "referenced_by": self.referenced_by
            }
            metadata_collection.update_one({"referenced_by": {"$exists": True}}, {"$set": referenced_by_document},
                                           upsert=True)
            print("Saved referenced_by document")

            print("Finished saving metadata to MongoDB")
