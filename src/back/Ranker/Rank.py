import time
import logging

from Indexer.IndexCreator import IndexCreator
from Preprocessor.DataCleaner import DataCleaner
from Ranker.Relevancy import Relevancy
from Basics.connection2 import MongoDBConnection

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class Rank:
    def __init__(self, db_name='M151', collection_name='Papers'):
        self.cleaner = DataCleaner()
        self.relevancy = Relevancy()
        self.indexer = IndexCreator()
        self.indexer.create_index()
        self.db_name = db_name
        self.collection_name = collection_name
        self.trie = self.indexer.index_dictionary
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_connection().get_database(self.db_name).get_collection(self.collection_name)

    def _get_ids(self, tokenized_query):
        start_time = time.time()
        results = set()
        for word in tokenized_query:
            _infos = self.trie.search(word)
            for info in _infos:
                results.add(info[0])
        end_time = time.time()
        time_diff = end_time - start_time
        logging.info(f"Time elapsed (get_ids): {time_diff} seconds")
        return results

    def _get_scores_cosine(self, user_query):
        start_time = time.time()
        results = self._get_ids(self.cleaner.cleanData(user_query))

        papers = self.collection.find(
            {"_id": {"$in": list(results)}}, {"title": 1, "abstract": 1, "URL": 1})
        results_dict = dict()
        for document in papers:
            title = document.get('title')[0]
            results_dict[document.get('_id')] = self.relevancy.cosine_similarity(title, user_query)
        end_time = time.time()
        time_diff = end_time - start_time
        logging.info(f"Time elapsed (get_scores): {time_diff} seconds")
        sorted_results = sorted(results_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_object_ids = [item[0] for item in sorted_results]
        return sorted_object_ids

    def _get_scores_sample(self, query):
        start_time = time.time()
        cleaned_query = self.cleaner.cleanData(query)
        scores = dict()
        for word in cleaned_query:
            _infos = self.trie.search(word)
            for info in _infos:
                if info[0] in scores:
                    scores[info[0]] += 1
                else:
                    scores[info[0]] = 1
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        end_time = time.time()
        time_diff = end_time - start_time
        logging.info(f"Time elapsed (_get_scores_sample): {time_diff} seconds")
        return [_id for _id, score in sorted_scores]

    def rank_documents_proximity_multi_terms(self, query, window_size, alpha=0.5):
        start_time = time.time()
        # Split the query into terms
        query_terms = query.split()

        # Initialize a dictionary to keep track of the score for each document
        document_scores = {}

        # Iterate over the query terms and posting lists in the inverted index
        for term in query_terms:
            posting_list = self.trie.search(term)

            # Iterate over the postings in the posting list
            for posting in posting_list:
                doc_id = posting[0]
                position = posting[1]

                # Check if this document has been scored before
                if doc_id not in document_scores:
                    document_scores[doc_id] = 0

                # Calculate the weight for this term based on its proximity to other query terms
                weight = 1

                # Check if previous terms in the query appear in the same document
                for i in range(max(0, query_terms.index(term) - window_size), query_terms.index(term)):
                    prev_term = query_terms[i]
                    prev_postings = self.trie.search(prev_term)
                    prev_positions = [p[1] for p in prev_postings if p[0] == doc_id]  # change it to take into consideration the correct order of the words

                    if prev_positions:
                        closest_prev_position = min(prev_positions, key=lambda x: abs(x - position))
                        prev_weight = alpha ** (query_terms.index(term) - i)
                        weight = prev_weight(1 / (abs(closest_prev_position - position) + 1))

                # Check if next terms in the query appear in the same document
                for i in range(query_terms.index(term) + 1,
                               min(len(query_terms), query_terms.index(term) + window_size + 1)):
                    next_term = query_terms[i]
                    next_postings = self.trie.search(next_term)
                    next_positions = [p[1] for p in next_postings if p[0] == doc_id]  # change it to take into consideration the correct order of the words

                    if next_positions:
                        closest_next_position = min(next_positions, key=lambda x: abs(x - position))
                        next_weight = alpha ** (i - query_terms.index(term))
                        weight = next_weight(1 / (abs(closest_next_position - position) + 1))

                # Add the weighted frequency of this term to the document's score
                document_scores[doc_id] += weight

        # Sort the documents by their scores in descending order
        results = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)
        end_time = time.time()
        time_diff = end_time - start_time
        logging.info(f"Time elapsed (rank_documents_proximity_multi_terms): {time_diff} seconds")
        return [_id for _id, score in results]

    def final_results(self, user_query):
        start_time = time.time()

        ids = self._get_scores_sample(user_query)
        # ids = self.rank_documents_proximity_multi_terms(user_query, 2)
        # ids = self._get_scores_cosine(user_query)

        # define the aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "_id": {"$in": ids}
                }
            },
            {
                "$addFields": {
                    "order": {"$indexOfArray": [ids, "$_id"]}
                }
            },
            {
                "$sort": {
                    "order": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "title": 1,
                    "abstract": 1,
                    "URL": 1
                }
            },
            {
                "$limit": 10000
            }
        ]

        results = list(self.collection.aggregate(pipeline))
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return results
