import unittest
from indexer import InfoClass  # Replace with the correct module


class TestInfoClass(unittest.TestCase):
    def setUp(self):
        """
        Set up a test instance of InfoClass to be used across multiple tests
        """
        self.test_type = 'test_type'
        self.test_position = 123
        self.test_docid = 456
        self.info_class = InfoClass(self.test_type, self.test_position, self.test_docid)

    def test_init(self):
        """
        Test the __init__ method of the InfoClass class
        """
        self.assertEqual(self.info_class._type, self.test_type)
        self.assertEqual(self.info_class._position, self.test_position)
        self.assertEqual(self.info_class._docid, self.test_docid)

    def test_json(self):
        """
        Test the __json__ method of the InfoClass class
        """
        expected_dict = {
            'type': self.test_type,
            'position': self.test_position,
            'docid': self.test_docid
        }
        self.assertEqual(self.info_class.__json__(), expected_dict)


if __name__ == '__main__':
    unittest.main()
