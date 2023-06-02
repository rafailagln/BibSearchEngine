import nltk
import string
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class DataCleaner:

    def __init__(self) -> None:
        super().__init__()
        nltk.download('stopwords')
        nltk.download('punkt')
        self._stop_words = set(stopwords.words('english'))

    def cleanData(self, data):
        data = self.__htmlStrip(data)
        data = self.__lowerString(data)
        data = self.__tokenizer(data)
        data = self.__punctuationDeletion(data)
        return data

    @staticmethod
    def __htmlStrip(data):
        return re.sub('<.*?>', ' ', data)

    @staticmethod
    def __lowerString(data):
        return data.lower()

    @staticmethod
    def __tokenizer(data):
        return word_tokenize(data)

    def __punctuationDeletion(self, data):
        return [word for word in data if word not in self._stop_words and word not in string.punctuation]
