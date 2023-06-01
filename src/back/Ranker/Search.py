import time
from collections import defaultdict

from indexer.index_creator import TITLE, ABSTRACT
from Preprocessor.DataCleaner import DataCleaner
from Ranker.RankingAlgorithms import BooleanInformationRetrieval, BM25F


class SearchEngine:

    def __init__(self, index, max_results):
        self.inverted_index = index.index_dictionary
        self.index_metadata = index.index_metadata
        self.cleaner = DataCleaner()
        self.max_results = max_results
        self.bir = BooleanInformationRetrieval(self.inverted_index, self.max_results)
        self.bm25f = BM25F(self.inverted_index, total_docs=self.index_metadata.total_docs)

    def search(self, query):
        final_scored_docs = defaultdict(float)
        cleaned_query = self.cleaner.cleanData(query)
        all_docs = list(self._count_results(cleaned_query))
        searching_docs = all_docs
        # Αdd AND-semantics of query to searching results
        # All words in the text must be present
        # searching_docs = list(self.add_and_semantics(cleaned_query, all_docs))

        # if none document have all words use all documents
        # if len(searching_docs) == 0:
        #     searching_docs = all_docs

        # if exists too many documents, cut them to threshold with BooleanSearch (+ referenced_by)
        print("Searching", len(searching_docs), " number of docs (before boolean)")
        start2_time = time.time()
        if len(searching_docs) > self.max_results:
            # add referenced_by to cut results
            searching_docs = self.bir.boolean_search(cleaned_query)
        end2_time = time.time()
        time_diff = end2_time - start2_time
        print("Time elapsed (BIR search):", time_diff, "seconds")

        end2_time = time.time()
        print("Searching", len(searching_docs), " number of docs (after boolean)")
        # rank documents with BM25F algorithm
        bm25f_scored_docs = self.bm25f.bm25f(searching_docs, cleaned_query, self._get_weight_dict(),
                                             self.index_metadata.length_field, self.index_metadata.average_length)

        # add referenced_by to ranking function
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
        start_time = time.time()
        ids = self.search(user_query)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return ids

    def _count_results(self, query_terms):
        docs = set()
        for word in query_terms:
            temp_docs = self.inverted_index.search(word)
            for doc_id, position, field in temp_docs:
                docs.add(doc_id)
        return docs

    # This function adds "soft" AND-semantics because it doesn't
    # take into consideration if the word is in the same field
    def add_and_semantics(self, query_terms, unique_docs):
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
        start_time = time.time()
        sorted_scores = sorted(documents.items(), key=lambda x: x[1], reverse=True)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Sorting (BM25F search):", time_diff, "seconds")
        return sorted_scores

    @staticmethod
    def _get_weight_dict():
        return {
            TITLE: 2,
            ABSTRACT: 1.2
        }

    def update_inverted_index(self, new_inverted_index):
        self.inverted_index = new_inverted_index

    def update_index_metadata(self, new_index_metadata):
        self.index_metadata = new_index_metadata

    def update_max_results(self, new_max_results):
        self.max_results = new_max_results
