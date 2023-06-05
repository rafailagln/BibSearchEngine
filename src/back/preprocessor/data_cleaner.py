import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class DataCleaner:
    def __init__(self) -> None:
        """
        Initializes the DataCleaner object and downloads necessary NLTK resources.
        """
        super().__init__()
        nltk.download('stopwords')
        nltk.download('punkt')
        self._stop_words = set(stopwords.words('english'))

    def clean_data(self, data):
        """
        Cleans the given data by performing several data cleaning operations.

        Args:
            data (str): The data to be cleaned.

        Returns:
            list: The cleaned data as a list of words.

        """
        data = self.__html_strip(data)
        data = self.__lower_string(data)
        data = self.__tokenizer(data)
        data = self.__punctuation_deletion(data)
        return data

    @staticmethod
    def __html_strip(data):
        """
        Removes HTML tags from the given data.

        Args:
            data (str): The data containing HTML tags.

        Returns:
            str: The data with HTML tags removed.

        """
        return re.sub('<.*?>', ' ', data)

    @staticmethod
    def __lower_string(data):
        """
        Converts the given data to lowercase.

        Args:
            data (str): The data to be converted.

        Returns:
            str: The lowercase version of the data.

        """
        return data.lower()

    @staticmethod
    def __tokenizer(data):
        """
        Tokenizes the given data into a list of words.

        Args:
            data (str): The data to be tokenized.

        Returns:
            list: A list of words from the data.

        """
        return word_tokenize(data)

    def __punctuation_deletion(self, data):
        """
        Removes stopwords and punctuation from the given data.

        Args:
            data (list): The data to be processed.

        Returns:
            list: The processed data with stopwords and punctuation removed.

        """
        return [word for word in data if word not in self._stop_words and word not in string.punctuation]
