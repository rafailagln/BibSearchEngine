import pymongo


class Reader:

    def __init__(self, connection_string) -> None:
        super().__init__()
        self._connectionString = connection_string

    def get_collection(self, db_name, collection_name):
        """
        Retrieves a collection from the MongoDB database.

        Inputs:
        - db_name: The name of the database.
        - collection_name: The name of the collection.

        Output:
        - The requested collection object.
        """
        client = pymongo.MongoClient(self._connectionString)
        db = client[db_name]
        collection = db[collection_name]
        return collection

    @staticmethod
    def read_collection(collection):
        """
        Reads all documents from the provided collection.

        Input:
        - collection: The collection to read documents from.

        Output:
        - A cursor object representing the result of the query.
        """
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1})

    @staticmethod
    def read_limited_collection(collection, limit):
        """
        Reads a limited number of documents from the provided collection.

        Inputs:
        - collection: The collection to read documents from.
        - limit: The maximum number of documents to retrieve.

        Output:
        - A cursor object representing the result of the query.
        """
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1}).limit(limit)
