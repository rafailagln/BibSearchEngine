import time

from Indexer.IndexCreator import IndexCreator, TITLE, ABSTRACT
from Preprocessor.DataCleaner import DataCleaner
from Ranker.RankingAlgorithms import BooleanInformationRetrieval, BM25F


class SearchEngine:

    def __init__(self, db, max_results):
        self.indexer = IndexCreator(db)
        self.indexer.create_index()
        self.inverted_index = self.indexer.index_dictionary
        self.index_metadata = self.indexer.index_metadata
        self.cleaner = DataCleaner()
        self.max_results = max_results
        self.bir = BooleanInformationRetrieval(self.inverted_index, self.max_results)
        self.bm25f = BM25F(self.inverted_index, total_docs=self.index_metadata.total_docs)
        self.db = db

    def search(self, query):
        start_time = time.time()
        cleaned_query = self.cleaner.cleanData(query)
        searching_docs = list(self._count_results(cleaned_query))

        print("Searching", len(searching_docs), " number of docs (before boolean)")
        # if exists too many documents, cut them to threshold with BooleanSearch
        start2_time = time.time()
        if len(searching_docs) > self.max_results:
            searching_docs = self.bir.boolean_search(cleaned_query)
        end2_time = time.time()
        time_diff = end2_time - start2_time
        print("Time elapsed (BIR search):", time_diff, "seconds")

        print("Searching", len(searching_docs), " number of docs (after boolean)")
        # rank documents with BM25F algorithm
        scored_docs = self.bm25f.bm25f(searching_docs, cleaned_query, self._get_weight_dict(),
                                       self.index_metadata.length_field, self.index_metadata.average_length)

        end_time = time.time()
        time_diff = end_time - end2_time
        print("Time elapsed (search):", time_diff, "seconds")
        return scored_docs

    def search_ids(self, user_query):
        start_time = time.time()
        ids = self.search(user_query)
        # results = self.db.get_titles_abstracts_urls(ids, True)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return ids

    def fetch_data(self, ids):
        return self.db.get_titles_abstracts_urls(ids, True)

    def _count_results(self, query_terms):
        docs = set()
        for word in query_terms:
            temp_docs = self.inverted_index.search(word)
            for doc_id, position, field in temp_docs:
                docs.add(doc_id)
        return docs

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