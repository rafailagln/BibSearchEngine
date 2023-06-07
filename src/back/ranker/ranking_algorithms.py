import heapq
import math
import time
from collections import defaultdict
from indexer.index_creator import TITLE, ABSTRACT
import concurrent.futures


def default_float():
    return defaultdict(float)


def default_inner():
    return defaultdict(default_float)


class BM25F:

    def __init__(self, inverted_index, total_docs):
        """
        Constructor method for the BM25F class.

        Args:
            inverted_index: The inverted index used for scoring.
            total_docs: The total number of documents in the collection.
        """
        self.inverted_index = inverted_index
        self.total_docs = total_docs

    def update_index(self, inverted_index):
        """
        Updates the inverted index used for scoring.

        Args:
            inverted_index: The updated inverted index.
        """
        self.inverted_index = inverted_index

    def update_total_docs(self, total_docs):
        """
        Updates the total number of documents in the collection.

        Args:
            total_docs: The updated total number of documents.
        """
        self.total_docs = total_docs

    def bm25f(self, docs, query_terms, fields_weight_dict, length_field, avg_lf):
        """
        Calculates the BM25F score for a list of documents and a query.
        The score is calculated for each field and then summed up. The final
        score is the sum of the scores of each field. The type of BM25F is:
        score(Q, D) = Σ [ (Wf * tf(qi, Ff, D)) * (k1_f + 1) ] /
                        [ Wf * tf(qi, Ff, D) + k1_f * (1 - b_f + b_f * Lf(D) / avgLf) ]

        Args:
            docs: List of document IDs to be scored.
            query_terms: List of terms in the query.
            fields_weight_dict: Dictionary containing the weight for each field.
            length_field: Dictionary with document IDs and the number of words in each field.
            avg_lf: Dictionary with the average length of each field.

        Returns:
            score: Dictionary of document IDs and their corresponding BM25F scores.
        """
        score = defaultdict(float)
        start_time = time.time()
        idf = self._idf_calculation(query_terms)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (idf calculation):", time_diff, "seconds")

        start_time = time.time()
        tf_c = self._tf_field_calculation(query_terms)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (TF_FIELD):", time_diff, "seconds")
        start_time = time.time()
        # from all doc_ids that we will score
        for doc_id in docs:
            temp_score = 0.0
            # from each field that we want to give a score
            for field in fields_weight_dict:
                # not all documents have all fields
                if length_field[str(doc_id)][str(field)] == 0:
                    continue
                factor = self._algorith_parameters()[field]["k1"] * (1 - self._algorith_parameters()[field]["b"] +
                                                                     self._algorith_parameters()[field]["b"] *
                                                                     (length_field[str(doc_id)][str(field)] /
                                                                      avg_lf[str(field)]))
                # for every term of the query
                for term in query_terms:
                    tf = fields_weight_dict[field] * tf_c[term][doc_id][field]
                    # if term do not exist in this field of document, we don't have to compute score...
                    if tf == 0:
                        continue
                    temp_score += idf[term] * ((tf * (self._algorith_parameters()[field]["k1"] + 1)) / (tf + factor))

            score[doc_id] = temp_score

        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (BM25F search):", time_diff, "seconds")

        return score

    def _idf_calculation(self, query_terms):
        """
        Calculates the IDF (Inverse Document Frequency) for each query term.
        The type of IDF used is: IDF(qi) = log((N - n(q_i) + 0.5) / (n(q_i) + 0.5))

        Args:
            query_terms: List of terms in the query.

        Returns:
            idf_dict: Dictionary containing the IDF value for each query term.
        """
        idf_dict = defaultdict(float)
        for word in query_terms:
            unique_docs = self._number_of_word_docs(word)
            idf_dict[word] = math.log((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5))
        return idf_dict

    def _idf(self, word):
        """
        Calculates the IDF (Inverse Document Frequency) for a single word.
        The type of IDF used is: IDF(qi) = log((N - n(q_i) + 0.5) / (n(q_i) + 0.5))

        Args:
            word: The word for which to calculate IDF.

        Returns:
            IDF value for the word.
        """
        unique_docs = self._number_of_word_docs(word)
        return math.log((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5))

    def _number_of_word_docs(self, word):
        """
        Calculates the unique number of documents containing a specific word.

        Args:
            word: The word for which to count the number of documents.

        Returns:
            The number of documents containing the word.
        """
        docs = self.inverted_index.search(word)
        unique_docs = set()
        for doc_id, position, field in docs:
            unique_docs.add(doc_id)
        return len(unique_docs)

    def _tf_field_calculation(self, query_terms):
        """
        Calculates the term frequency (TF) for each query term and field.

        Args:
            query_terms: List of terms in the query.

        Returns:
            tf_results: Dictionary containing the TF value for each query term, document ID, and field.
        """
        tf_results = defaultdict(default_inner)
        for word in query_terms:
            docs = self.inverted_index.search(word)
            for doc_id, _, field in docs:
                tf_results[word][doc_id][field] += 1
        return tf_results

    def _tf_field(self, word, _field, field_length):
        """
        Calculates the term frequency (TF) for a single word in a specific field (TITLE or ABSTRACT).

        Args:
            word: The word for which to calculate TF.
            _field: The field in which to calculate TF.
            field_length: The length of the field.

        Returns:
            The TF value for the word in the field.
        """
        docs = self.inverted_index.search(word)
        counter = 0
        for doc_id, position, field in docs:
            if field == _field:
                counter += 1
        return counter / field_length

    @staticmethod
    def _algorith_parameters():
        """
        Returns the BM25F algorithm parameters for fields TITLE and ABSTRACT.

        Returns:
            Dictionary containing the algorithm parameters for each field.
        """
        return {
            TITLE: {
                "k1": 1.2,
                "b": 0.9
            },
            ABSTRACT: {
                "k1": 0.6,
                "b": 0.2
            }
        }


class BooleanInformationRetrieval:

    def __init__(self, inverted_index, max_results):
        """
        Constructor method for the BooleanInformationRetrieval class.

        Args:
            inverted_index: The inverted index used for searching.
            max_results: The maximum number of results to return.
        """
        self.index = inverted_index
        self.max_results = max_results

    def update_index(self, inverted_index):
        """
        Method to update the inverted index.

        Args:
            inverted_index: The new inverted index to be used.
        """
        self.index = inverted_index

    def update_max_results(self, max_results):
        """
        Method to update the maximum number of results to return.

        Args:
            max_results: The new maximum number of results.
        """
        self.max_results = max_results

    def boolean_search(self, query):
        """
        Method to perform boolean search based on a query. Boolean search
        is performed by finding the documents that contain all the words
        in the query. The documents are then ranked by the number of words
        they contain.

        Args:
            query: A list of words representing the search query.

        Returns:
            A list of document IDs that match the query, sorted by relevance.
        """
        start_time = time.time()
        results = defaultdict(int)

        # loop for every word of the query
        for word in query:
            # get info from index
            index_results = self.index.search(word)
            # loop for all nodes in the index for that word
            for doc_id, position, field in index_results:
                results[doc_id] += 1

        sorted_scores = heapq.nlargest(self.max_results, results.items(), key=lambda x: x[1])
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (Boolean search):", time_diff, "seconds")
        return [doc_id for doc_id, score in sorted_scores]
