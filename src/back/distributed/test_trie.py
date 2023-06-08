import unittest
from db.connection import MongoDBConnection
from distributed.trie import TrieIndex


class TestTrieIndex(unittest.TestCase):
    def setUp(self):
        self.trie_index = TrieIndex('TestDB', 'TestIndex')

    def tearDown(self):
        # Drop the database after each test
        with MongoDBConnection() as conn:
            mongo = conn.get_connection()
            mongo.drop_database(self.trie_index.db_name)

        # Clear the trie after each test
        self.trie_index = None

    def test_insert_and_search(self):
        self.trie_index.insert('key1', 'value1')
        values = self.trie_index.search('key1')
        self.assertEqual(values, ['value1'])

    def test_delete(self):
        self.trie_index.insert('key1', 'value1')
        self.trie_index.delete('key1')
        values = self.trie_index.search('key1')
        self.assertEqual(values, [])

    def test_get_keys(self):
        self.trie_index.insert('key1', 'value1')
        self.trie_index.insert('key2', 'value2')
        keys = self.trie_index.get_keys()
        self.assertEqual(set(keys), {'key1', 'key2'})

    def test_save_and_load(self):
        self.trie_index.insert('key1', 'value1')
        self.trie_index.insert('key2', 'value2')
        self.trie_index.save()

        new_trie_index = TrieIndex('TestDB', 'TestIndex')
        new_trie_index.load()

        keys = new_trie_index.get_keys()
        self.assertEqual(set(keys), {'key1', 'key2'})


if __name__ == '__main__':
    unittest.main()
