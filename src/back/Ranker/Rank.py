import heapq
import time
from collections import defaultdict

from Basics.connection2 import MongoDBConnection
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

    def __init__(self, db_name='M151', collection_name='Papers'):
        self.indexer = IndexCreator()
        self.indexer.create_index()
        self.db_name = db_name
        self.collection_name = collection_name
        self.index_dictionary = self.indexer.index_dictionary
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_connection().get_database(self.db_name).get_collection(self.collection_name)
        self.cleaner = DataCleaner()

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
            }
        ]

        results = list(self.collection.aggregate(pipeline))
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (final_results):", time_diff, "seconds")
        return results
