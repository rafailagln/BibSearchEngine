import time
from collections import defaultdict

from indexer.index_creator import TITLE, ABSTRACT
from preprocessor.data_cleaner import DataCleaner
from ranker.BM25FParallel import BM25FParallel
from ranker.ranking_algorithms import BooleanInformationRetrieval, BM25F


class SearchEngine:

    def __init__(self, index, max_results):
        """
        Constructor method for the SearchEngine class.

        Args:
            index: The index object containing the inverted index and index metadata.
            max_results: The maximum number of results to return.
        """
        self.inverted_index = index.index_dictionary
        self.index_metadata = index.index_metadata
        self.cleaner = DataCleaner()
        self.max_results = max_results
        self.bir = BooleanInformationRetrieval(self.inverted_index, self.max_results)
        self.bm25f = BM25FParallel(self.inverted_index, total_docs=self.index_metadata.total_docs)

    def search(self, query):
        """
        'search' performs a search operation using the ranking algorithm BM25F and the number of 'referenced_by'.

        Args:
            query (str): A string representing the search query.

        Returns:
            defaultdict: A defaultdict of float values. Each key in the dictionary corresponds to a document,
                         and the value represents the final score assigned to that document based on the ranking algorithm.

        Steps:
            1. Initialize an empty defaultdict called 'final_scored_docs' to store the final scores of documents.
            2. Clean the query by calling the 'cleanData' method of the 'cleaner' object associated with the current
               instance. Store the result in 'cleaned_query'.
            3. Call the '_count_results' method, passing 'cleaned_query' as an argument, to obtain a list of 'all_docs'.
            4. Assign 'all_docs' to 'searching_docs', indicating that all documents will be considered initially.
            5. If the number of documents in 'searching_docs' exceeds the maximum threshold ('max_results'), perform a
               boolean search using the 'boolean_search' method of the 'bir' object, passing 'cleaned_query' as an
               argument. Replace 'searching_docs' with the result.
            6. Rank the documents in 'searching_docs' using the 'bm25f' method. The ranking takes into account 'cleaned_query',
               a weight dictionary obtained from the '_get_weight_dict' method, and the 'length_field' and 'average_length'
               attributes of 'index_metadata'.
            7. Iterate over each document in 'searching_docs' and calculate the final score using a combination of the BM25F score
               and the referenced_by score. Store the final score in 'final_scored_docs'.
        """
        final_scored_docs = defaultdict(float)
        cleaned_query = self.cleaner.clean_data(query)
        all_docs = list(self._count_results(cleaned_query))
        searching_docs = all_docs

        # Αdd AND-semantics of query to searching results
        # All words in the text must be present
        # searching_docs = list(self.add_and_semantics(cleaned_query, all_docs))

        # if none document have all words use all documents
        # if len(searching_docs) == 0:
        #     searching_docs = all_docs

        # if there are too many documents, cut them to the threshold with BooleanSearch (+ referenced_by)
        print("Searching", len(searching_docs), "number of docs (before boolean)")
        start2_time = time.time()
        if len(searching_docs) > self.max_results:
            # add referenced_by to cut results
            searching_docs = self.bir.boolean_search(cleaned_query)
        end2_time = time.time()
        time_diff = end2_time - start2_time
        print("Time elapsed (BIR search):", time_diff, "seconds")

        end2_time = time.time()
        print("Searching", len(searching_docs), "number of docs (after boolean)")

        # rank documents with BM25F algorithm
        bm25f_scored_docs = self.bm25f.bm25f(searching_docs, cleaned_query, self._get_weight_dict(),
                                             self.index_metadata.length_field, self.index_metadata.average_length)

        # add referenced_by to the ranking function
        for doc in searching_docs:
            final_score = 0.0
            final_score += bm25f_scored_docs[doc] * 0.85
            final_score += self.index_metadata.referenced_by[doc] * 0.15
            final_scored_docs[doc] = final_score

        end_time = time.time()
        time_diff = end_time - end2_time
        print("Time elapsed (search):", time_diff, "seconds")

        # return bm25f_scored_docs
        return final_scored_docs

    def search_ids(self, user_query):
        """
        Takes a user query as input and returns a list of document IDs that contain the query terms.

        Args:
            user_query: A string containing the user query.

        Returns:
            ids: A list of document IDs that contain the query terms.
        """
        start_time = time.time()
        ids = self.search(user_query)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return ids

    def _count_results(self, query_terms):
        """
        Counts the number of unique documents containing any of the given query terms.

        Args:
            query_terms: A list of query terms to search for.

        Returns:
            docs: A set of document IDs that contain at least one of the query terms.
        """
        docs = set()
        for word in query_terms:
            temp_docs = self.inverted_index.search(word)
            for doc_id, position, field in temp_docs:
                docs.add(doc_id)
        return docs

    def add_and_semantics(self, query_terms, unique_docs):
        """
        Calculates the AND semantics between a given list of query terms and a set of unique documents.
        It uses an inverted index to retrieve the posting lists for each query term, and then counts the
        number of occurrences of each document ID. The function returns a list of document IDs that contain
        all the query terms.

        Args:
            query_terms: A list of query terms.
            unique_docs: A list of unique document IDs.

        Returns:
            A list of document IDs that contain all the query terms.
        """
        docs = {key: 0 for key in unique_docs}
        for word in query_terms:
            previous_doc = -1
            posting_list_docs = self.inverted_index.search(word)
            for doc_id, position, field in posting_list_docs:
                if doc_id != previous_doc:
                    docs[doc_id] += 1
                    previous_doc = doc_id
                else:
                    continue
        return [key for key, value in docs.items() if value == len(query_terms)]

    @staticmethod
    def sort_documents(documents):
        """
        'sort_documents' takes a dictionary of documents as input and returns a list of tuples 'sorted_scores'.

        Args:
            documents (dict): A dictionary containing document names as keys and their corresponding scores as values.
                              The scores are used to determine the sorting order.

        Returns:
            list: A list of tuples, where each tuple consists of a document name and its score. The list is sorted
                  in descending order based on the scores.

        Functionality:
            Sorts the 'documents' dictionary based on the values (scores) using the sorted() function and a lambda
            function as the key parameter. The lambda function extracts the second element (index 1) from each key-value
            pair in 'documents', which represents the score.
            The sorting is done in reverse order (from highest to lowest) by setting the reverse parameter to True.
            Finally, the function returns the 'sorted_scores' list.

        Example Usage:
            sorted_scores = sort_documents({'doc1': 0.8, 'doc2': 0.6, 'doc3': 0.9})
            print(sorted_scores)
            # Output: [('doc3', 0.9), ('doc1', 0.8), ('doc2', 0.6)]
        """
        start_time = time.time()
        sorted_scores = sorted(documents.items(), key=lambda x: x[1], reverse=True)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Sorting (BM25F search):", time_diff, "seconds")
        return sorted_scores

    @staticmethod
    def _get_weight_dict():
        """
        Returns a dictionary with weights assigned to different components.
        """
        return {
            TITLE: 2,
            ABSTRACT: 1.5
        }

    def update_inverted_index(self, new_inverted_index):
        """
        Updates the inverted index of the SearchEngine instance.

        Args:
            new_inverted_index: The new inverted index to be assigned.

        Returns:
            None
        """
        self.inverted_index = new_inverted_index

    def update_index_metadata(self, new_index_metadata):
        """
        Updates the index metadata with the provided new_index_metadata.

        Args:
            new_index_metadata: A dictionary or object containing the new index metadata.

        Returns:
            None
        """
        self.index_metadata = new_index_metadata

    def update_max_results(self, new_max_results):
        """
        Updates the max_results attribute.

        Args:
            new_max_results: The new value to assign to the max_results attribute.

        Returns:
            None
        """
        self.max_results = new_max_results
