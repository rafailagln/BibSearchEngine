import pymongo


class Reader:

    def __init__(self, connection_string) -> None:
        super().__init__()
        self._connectionString = connection_string

    def get_collection(self, db_name, collection_name):
        client = pymongo.MongoClient(self._connectionString)
        db = client[db_name]
        collection = db[collection_name]
        return collection

    @staticmethod
    def read_collection(collection):
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1})

    @staticmethod
    def read_limited_collection(collection, limit):
        return collection.find({}, {"_id": 1, "title": 1, "abstract": 1}).limit(limit)
