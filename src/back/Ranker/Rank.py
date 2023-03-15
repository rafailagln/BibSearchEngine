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
        self.index = self.indexer.index_dictionary
        self.mongo = MongoDBConnection()
        self.collection = self.mongo.get_connection().get_database(self.db_name).get_collection(self.collection_name)

    def _get_ids(self, tokenized_query):
        start_time = time.time()
        results = set()
        for word in tokenized_query:
            if word in self.index:
                _infos = self.index[word]
                for info in _infos:
                    results.add(info._docid)
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
        cleaned_query = self.cleaner.cleanData(query)
        scores = dict()
        for word in cleaned_query:
            if word in self.index:
                for node in self.index[word]:
                    if node._docid in scores:
                        scores[node._docid] += 1
                    else:
                        scores[node._docid] = 1
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [_id for _id, score in sorted_scores]

    def final_results(self, user_query):
        start_time = time.time()

        # ids = self._get_scores_sample(user_query)
        ids = self._get_scores_cosine(user_query)

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
        logging.info("Time elapsed (final_results):", time_diff, "seconds")
        return results
