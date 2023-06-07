import unittest
from preprocessor.data_cleaner import DataCleaner  # Replace with the correct module


class TestDataCleaner(unittest.TestCase):
    def setUp(self):
        """
        Set up a test instance of DataCleaner to be used across multiple tests
        """
        self.data_cleaner = DataCleaner()

    def test_html_strip(self):
        """
        Test the __html_strip method of the DataCleaner class
        """
        input_data = "<html><body><h1>  Test data</h1></body></html>"
        expected_output = str("     Test data   ")
        self.assertEqual(self.data_cleaner._DataCleaner__html_strip(input_data), expected_output)

    def test_lower_string(self):
        """
        Test the __lower_string method of the DataCleaner class
        """
        input_data = "TeSt DaTa"
        expected_output = "test data"
        self.assertEqual(self.data_cleaner._DataCleaner__lower_string(input_data), expected_output)

    def test_tokenizer(self):
        """
        Test the __tokenizer method of the DataCleaner class
        """
        input_data = "test data"
        expected_output = ['test', 'data']
        self.assertEqual(self.data_cleaner._DataCleaner__tokenizer(input_data), expected_output)

    def test_punctuation_deletion(self):
        """
        Test the __punctuation_deletion method of the DataCleaner class
        """
        input_data = ['test', 'data', ',', 'is', 'this', '!']
        expected_output = ['test', 'data']
        self.assertEqual(self.data_cleaner._DataCleaner__punctuation_deletion(input_data), expected_output)

    def test_clean_data(self):
        """
        Test the clean_data method of the DataCleaner class
        """
        input_data = "<html><body><h1>  Test data, is this!</h1></body></html>"
        expected_output = ['test', 'data']
        self.assertEqual(self.data_cleaner.clean_data(input_data), expected_output)


if __name__ == '__main__':
    unittest.main()
