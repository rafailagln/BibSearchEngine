import pymongo


class Reader:
    def __init__(self, connection_string) -> None:
        """
        Initializes a Reader object.

        Args:
            connection_string (str): The connection string for MongoDB.

        Returns:
            None
        """
        super().__init__()
        self._connectionString = connection_string

    def get_collection(self, db_name, collection_name):
        """
        Retrieves a collection from the MongoDB database.

        Args:
            db_name (str): The name of the database.
            collection_name (str): The name of the collection.

        Returns:
            pymongo.collection.Collection: The requested collection object.
        """
        client = pymongo.MongoClient(self._connectionString)
        db = client[db_name]
        collection = db[collection_name]
        return collection

    @staticmethod
    def read_collection(collection):
        """
        Reads all documents from the provided collection.

        Args:
            collection (pymongo.collection.Collection): The collection to read documents from.

        Returns:
            pymongo.cursor.Cursor: A cursor object representing the result of the query.
        """
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1})

    @staticmethod
    def read_limited_collection(collection, limit):
        """
        Reads a limited number of documents from the provided collection.

        Args:
            collection (pymongo.collection.Collection): The collection to read documents from.
            limit (int): The maximum number of documents to retrieve.

        Returns:
            pymongo.cursor.Cursor: A cursor object representing the result of the query.
        """
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1}).limit(limit)
