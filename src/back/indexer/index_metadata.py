from collections import defaultdict
from db.connection import MongoDBConnection


class Metadata:

    def __init__(self, db_name='M151', metadata_collection='Metadata'):
        """
        Initializes the Metadata object.

        Args:
            db_name (str): The name of the MongoDB database.
            metadata_collection (str): The name of the collection in the MongoDB database.

        Returns:
            None
        """
        self.length_field = defaultdict(lambda: defaultdict(int))
        self.average_length = defaultdict(float)
        self.referenced_by = defaultdict(int)
        self.total_docs = 0
        self.db_name = db_name
        self.metadata_collection = metadata_collection

    def update_doc_num(self):
        """
        Updates the total number of documents.

        Returns:
            None
        """
        self.total_docs += 1

    def add_doc_length_field(self, doc_id, length, field):
        """
        Adds the length of a specific field in a document.

        Args:
            doc_id (str): The ID of the document.
            length (int): The length of the field.
            field (str): The name of the field.

        Returns:
            None
        """
        self.length_field[str(doc_id)][str(field)] = length

    def increase_average_length(self, length, field):
        """
        Increases the average length of a specific field.

        Args:
            length (int): The length to be added to the average.
            field (str): The name of the field.

        Returns:
            None
        """
        self.average_length[str(field)] += length

    def calculate_average_length(self):
        """
        Calculates the average length for each field.

        Returns:
            None
        """
        for field in self.average_length.keys():
            self.average_length[field] /= self.total_docs

    def add_referenced_by(self, doc_id, referenced):
        """
        Adds the number of times a document is referenced by other documents.

        Args:
            doc_id (str): The ID of the document.
            referenced (int): The number of references.

        Returns:
            None
        """
        self.referenced_by[str(doc_id)] = referenced

    def normalize_referenced_by(self):
        """
        Normalizes the referenced_by values.

        Returns:
            None
        """
        max_val = max(self.referenced_by.values())
        min_val = min(self.referenced_by.values())

        for key in self.referenced_by:
            self.referenced_by[key] -= min_val

        # Divide each value by the range
        range_val = max_val - min_val
        for key in self.referenced_by:
            self.referenced_by[key] /= range_val

    def set_total_docs(self, num):
        """
        Sets the total number of documents.

        Args:
            num (int): The total number of documents.

        Returns:
            None
        """
        self.total_docs = num

    def load(self):
        """
        Loads the metadata from the MongoDB collection.

        Returns:
            None
        """
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
        """
        Saves the metadata to the MongoDB collection.

        Returns:
            None
        """
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            metadata_collection = mongo.get_database(self.db_name).get_collection(self.metadata_collection)

            # Save each value in length_field as a separate document
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
