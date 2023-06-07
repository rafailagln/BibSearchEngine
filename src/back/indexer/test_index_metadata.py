import unittest
from unittest.mock import patch, Mock
from db.connection import MongoDBConnection
from indexer import Metadata


class TestMetadata(unittest.TestCase):

    @patch('db.connection.MongoDBConnection.get_connection', return_value=Mock())
    def setUp(self, mock_get_connection):
        self.db_name = 'testDB'
        self.metadata_collection = 'testMetadata'
        self.metadata = Metadata(self.db_name, self.metadata_collection)

    def test_update_doc_num(self):
        self.metadata.update_doc_num()
        self.assertEqual(self.metadata.total_docs, 1)

    def test_add_doc_length_field(self):
        self.metadata.add_doc_length_field('doc1', 10, 'field1')
        self.assertEqual(self.metadata.length_field['doc1']['field1'], 10)

    def test_increase_average_length(self):
        self.metadata.increase_average_length(10, 'field1')
        self.assertEqual(self.metadata.average_length['field1'], 10)

    def test_calculate_average_length(self):
        self.metadata.increase_average_length(10, 'field1')
        self.metadata.increase_average_length(10, 'field1')
        self.metadata.update_doc_num()
        self.metadata.update_doc_num()
        self.metadata.calculate_average_length()
        self.assertEqual(self.metadata.average_length['field1'], 10)

    def test_add_referenced_by(self):
        self.metadata.add_referenced_by('doc1', 5)
        self.assertEqual(self.metadata.referenced_by['doc1'], 5)

    def test_normalize_referenced_by(self):
        self.metadata.add_referenced_by('doc1', 10)
        self.metadata.add_referenced_by('doc2', 5)
        self.metadata.normalize_referenced_by()
        self.assertEqual(self.metadata.referenced_by['doc1'], 1)
        self.assertEqual(self.metadata.referenced_by['doc2'], 0)

    def test_set_total_docs(self):
        self.metadata.set_total_docs(100)
        self.assertEqual(self.metadata.total_docs, 100)


# These load/save tests are mocked because we don't want to actually hit the DB in a unit test.
# This just checks that the function calls the expected DB functions with the expected parameters.
# You may need to adjust these mocks based on how your MongoDBConnection class actually works.

    # @patch('db.connection.MongoDBConnection.get_connection', return_value=Mock())
    # def test_load(self, mock_get_connection):
    #     mock_db = mock_get_connection.return_value.get_database.return_value
    #     mock_collection = mock_db.get_collection.return_value
    #     mock_collection.find.return_value = []
    #     mock_collection.find_one.return_value = None
    #     self.metadata.load()
    #     mock_get_connection.assert_called_once()
    #     mock_db.get_collection.assert_called_once_with(self.metadata_collection)

    # @patch('db.connection.MongoDBConnection.get_connection', return_value=Mock())
    # def test_save(self, mock_get_connection):
    #     mock_db = mock_get_connection.return_value.get_database.return_value
    #     mock_collection = mock_db.get_collection.return_value
    #     self.metadata.save()
    #     mock_get_connection.assert_called_once()
    #     mock_db.get_collection.assert_called_once_with(self.metadata_collection)


if __name__ == '__main__':
    unittest.main()
