import unittest
from pymongo import MongoClient
from unittest.mock import patch, Mock
from indexer import Reader
from mongomock import MongoClient as MockedClient


class TestReader(unittest.TestCase):
    def setUp(self):
        self.connection_string = "mongodb://localhost:27017"
        self.reader = Reader(self.connection_string)
        self.db_name = "test_db"
        self.collection_name = "test_collection"
        self.mocked_client = MockedClient()

    @patch('pymongo.MongoClient', return_value=MockedClient())
    def test_get_collection(self, mock_client):
        mock_db = self.mocked_client[self.db_name]
        mock_collection = mock_db[self.collection_name]
        collection = self.reader.get_collection(self.db_name, self.collection_name)
        self.assertEqual(collection.name, mock_collection.name)

    def test_read_collection(self):
        mock_collection = self.mocked_client[self.db_name][self.collection_name]
        mock_collection.find = Mock()
        self.reader.read_collection(mock_collection)
        mock_collection.find.assert_called_with({}, {"_id": 1, "title": 1, "abstract": 1})

    def test_read_limited_collection(self):
        limit = 5
        mock_collection = self.mocked_client[self.db_name][self.collection_name]
        mock_collection.find = Mock(return_value=Mock(limit=Mock()))
        self.reader.read_limited_collection(mock_collection, limit)
        mock_collection.find.assert_called_with({}, {"_id": 1, "title": 1, "abstract": 1})
        mock_collection.find().limit.assert_called_with(limit)


if __name__ == "__main__":
    unittest.main()
