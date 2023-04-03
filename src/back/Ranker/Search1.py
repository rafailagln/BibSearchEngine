import heapq
import time
from collections import defaultdict

from Indexer.IndexCreator import TITLE, IndexCreator
from Preprocessor.DataCleaner import DataCleaner


def calculate_score(field, count):
    field_weight = 2 if field == TITLE else 1
    return field_weight * count


def calculate_proximity(positions_dict):
    proximity_score = 0
    for field, positions in positions_dict.items():
        if len(positions) < 2:
            continue
        positions.sort()
        min_distance = float('inf')
        for i in range(1, len(positions)):
            distance = positions[i] - positions[i - 1]
            min_distance = min(min_distance, distance)
        proximity_score += 1 / min_distance
    return proximity_score


class SearchEngine:

    def __init__(self, db):
        self.indexer = IndexCreator(db)
        self.indexer.create_index()
        self.index_dictionary = self.indexer.index_dictionary
        self.cleaner = DataCleaner()
        self.db = db

    def search(self, query, max_results=10000):
        start_time = time.time()
        cleaned_query = self.cleaner.cleanData(query)
        results = defaultdict(lambda: defaultdict(int))
        scores = defaultdict(int)
        doc_positions = defaultdict(lambda: defaultdict(list))

        # loop for every word of the query
        for word in cleaned_query:
            # get info from index
            index_results = self.index_dictionary.search(word)
            # loop for all rows in the index for that word
            for doc_id, position, field in index_results:
                results[doc_id][field] += 1
                doc_positions[doc_id][field].append(position)

        for doc_id in results.keys():
            proximity_score = calculate_proximity(doc_positions[doc_id])
            for field, count in results[doc_id].items():
                scores[doc_id] += calculate_score(field, count) * proximity_score

        sorted_scores = heapq.nlargest(max_results, scores.items(), key=lambda x: x[1])
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (search):", time_diff, "seconds")
        return [doc_id for doc_id, score in sorted_scores]

    def final_results(self, user_query):
        start_time = time.time()

        ids = self.search(user_query)
        results = self.db.get_titles_abstracts_urls(ids, True)

        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return results
