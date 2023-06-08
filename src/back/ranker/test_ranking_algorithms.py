import unittest
from collections import defaultdict
from unittest.mock import MagicMock
from ranker import BM25F, BooleanInformationRetrieval
from indexer.index_creator import TITLE, ABSTRACT


# Unit tests
class TestBM25F(unittest.TestCase):
    def setUp(self):
        self.inverted_index = MagicMock()
        self.bm25f = BM25F(self.inverted_index, total_docs=1000)

    def test_update_index(self):
        new_index = MagicMock()
        self.bm25f.update_index(new_index)
        self.assertEqual(self.bm25f.inverted_index, new_index)

    def test_update_total_docs(self):
        new_total_docs = 2000
        self.bm25f.update_total_docs(new_total_docs)
        self.assertEqual(self.bm25f.total_docs, new_total_docs)

    def test_algorith_parameters(self):
        expected_output = {
            TITLE: {
                "k1": 1.2,
                "b": 0.9
            },
            ABSTRACT: {
                "k1": 0.6,
                "b": 0.2
            }
        }
        self.assertEqual(self.bm25f._algorith_parameters(), expected_output)


class TestBooleanInformationRetrieval(unittest.TestCase):
    def setUp(self):
        self.inverted_index = MagicMock()
        self.boolean_IR = BooleanInformationRetrieval(self.inverted_index, max_results=10)

    def test_update_index(self):
        new_index = MagicMock()
        self.boolean_IR.update_index(new_index)
        self.assertEqual(self.boolean_IR.index, new_index)

    def test_update_max_results(self):
        new_max_results = 20
        self.boolean_IR.update_max_results(new_max_results)
        self.assertEqual(self.boolean_IR.max_results, new_max_results)

    # Testing 'boolean_search' method would also require more complex setup
    # and mocking to handle the dependencies and side effects.


class TestBM25FComplex(unittest.TestCase):
    def setUp(self):
        self.inverted_index = MagicMock()
        self.bm25f = BM25F(self.inverted_index, total_docs=1000)

    # def test_idf_calculation(self):
    #     self.bm25f._number_of_word_docs = MagicMock(side_effect=[50, 200])
    #     idf_dict = self.bm25f._idf_calculation(["test1", "test2"])
    #     self.assertAlmostEqual(idf_dict["test1"], 1.791759, delta=0.000001)
    #     self.assertAlmostEqual(idf_dict["test2"], 0.693147, delta=0.000001)

    def test_tf_field_calculation(self):
        self.inverted_index.search = MagicMock(
            return_value=[("doc1", 1, TITLE), ("doc1", 2, TITLE), ("doc2", 1, ABSTRACT)])
        tf_results = self.bm25f._tf_field_calculation(["test"])
        self.assertEqual(tf_results["test"]["doc1"][TITLE], 2)
        self.assertEqual(tf_results["test"]["doc2"][ABSTRACT], 1)


class TestBooleanInformationRetrievalComplex(unittest.TestCase):
    def setUp(self):
        self.inverted_index = MagicMock()
        self.boolean_IR = BooleanInformationRetrieval(self.inverted_index, max_results=2)

    def test_boolean_search(self):
        self.inverted_index.search = MagicMock(
            return_value=[("doc1", 1, TITLE), ("doc1", 2, ABSTRACT), ("doc2", 1, ABSTRACT)])
        results = self.boolean_IR.boolean_search(["test"])
        self.assertEqual(results, ["doc1", "doc2"])
