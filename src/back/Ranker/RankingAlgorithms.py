import heapq
import math
import time
from collections import defaultdict
from Indexer.IndexCreator import TITLE, ABSTRACT
import concurrent.futures


# def compute_doc_score(docs, query_terms, fields_weight_dict, length_field, avg_lf, idf, tf_c, k1, b):
#     score = defaultdict(float)
#     for doc_id in docs:
#         temp_score = 0.0
#         for field in fields_weight_dict:
#             if length_field[str(doc_id)][str(field)] == 0:
#                 continue
#             factor = k1 * (1 - b + b * (length_field[str(doc_id)][str(field)] / avg_lf[str(field)]))
#             for term in query_terms:
#                 tf = fields_weight_dict[field] * tf_c[term][doc_id][field]
#                 if tf == 0:
#                     continue
#                 temp_score += idf[term] * ((tf * (k1 + 1)) / (tf + factor))
#
#         score[doc_id] = temp_score
#
#     return score


class BM25F:

    def __init__(self, inverted_index, total_docs):
        self.inverted_index = inverted_index
        self.total_docs = total_docs

    def update_index(self, inverted_index):
        self.inverted_index = inverted_index

    def update_total_docs(self, total_docs):
        self.total_docs = total_docs

    '''
    score(Q, D) = Σ [ (Wf * tf(qi, Ff, D)) * (k1 + 1) ] / [ Wf * tf(qi, Ff, D) + k1 * (1 - b + b * Lf(D) / avgLf) ]
    length_field is a dictionary with doc_ids and fields. For every doc_id it has the number of the length of each field 
    '''

    def bm25f(self, docs, query_terms, fields_weight_dict, length_field, avg_lf):
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

    # def bm25f(self, docs, query_terms, fields_weight_dict, length_field, avg_lf, k1=1.2, b=0.75, chunk_size=2000):
    #     score = defaultdict(float)
    #     start_time = time.time()
    #     idf = self._idf_calculation(query_terms)
    #     end_time = time.time()
    #     time_diff = end_time - start_time
    #     print("Time elapsed (idf calculation):", time_diff, "seconds")
    #
    #     start_time = time.time()
    #     tf_c = self._tf_field_calculation(query_terms)
    #     end_time = time.time()
    #     time_diff = end_time - start_time
    #     print("Time elapsed (TF_FIELD):", time_diff, "seconds")
    #
    #     # Split the list of documents into chunks
    #     chunks = [docs[i:i + chunk_size] for i in range(0, len(docs), chunk_size)]
    #
    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         futures = []
    #         for chunk in chunks:
    #             future = executor.submit(compute_doc_score, chunk, query_terms, fields_weight_dict, length_field,
    #                                      avg_lf, idf, tf_c, k1, b)
    #             print(f"Sending chunk")
    #             futures.append(future)
    #
    #         for future in concurrent.futures.as_completed(futures):
    #             chunk_score = future.result()
    #             print(f"Got result chunk")
    #             score.update(chunk_score)
    #
    #     end_time = time.time()
    #     time_diff = end_time - start_time
    #     print("Time elapsed (BM25F search):", time_diff, "seconds")

    #     return score

    def _idf_calculation(self, query_terms):
        idf_dict = defaultdict(float)
        for word in query_terms:
            unique_docs = self._number_of_word_docs(word)
            idf_dict[word] = math.log((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5))
        return idf_dict

    def _idf(self, word):
        unique_docs = self._number_of_word_docs(word)
        return math.log((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5))
        # return math.log(self.total_docs / unique_docs)

    def _number_of_word_docs(self, word):
        docs = self.inverted_index.search(word)
        unique_docs = set()
        for doc_id, position, field in docs:
            unique_docs.add(doc_id)
        return len(unique_docs)

    def _tf_field_calculation(self, query_terms):
        tf_results = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        for word in query_terms:
            docs = self.inverted_index.search(word)
            for doc_id, _, field in docs:
                tf_results[word][doc_id][field] += 1
        return tf_results

    def _tf_field(self, word, _field, field_length):
        docs = self.inverted_index.search(word)
        counter = 0
        for doc_id, position, field in docs:
            if field == _field:
                counter += 1
        return counter / field_length

    @staticmethod
    def _algorith_parameters():
        return {
            TITLE: {
                "k1": 1.2,
                "b": 0.65
            },
            ABSTRACT: {
                "k1": 1.4,
                "b": 0.2
            }
        }


class BooleanInformationRetrieval:

    def __init__(self, inverted_index, max_results):
        self.index = inverted_index
        self.max_results = max_results

    def update_index(self, inverted_index):
        self.index = inverted_index

    def update_max_results(self, max_results):
        self.max_results = max_results

    def boolean_search(self, query):
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
