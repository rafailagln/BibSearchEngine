import heapq
import math
import time
from collections import defaultdict


def tokenize(text):
    return text.lower().split()


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

    def bm25f(self, docs, query_terms, fields_weight_dict, length_field, avg_lf, k1=1.2, b=0.75):
        score = defaultdict(float)
        start_time = time.time()
        idf = self._idf_calculation(query_terms)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (idf calculation):", time_diff, "seconds")

        start_time = time.time()
        tf_c = self._tf_field_calculation(query_terms)
        # from all doc_ids that we will score
        for doc_id in docs:
            temp_score = 0.0
            # from each field that we want to give a score
            for field in fields_weight_dict:
                # not all documents have all fields
                if length_field[str(doc_id)][str(field)] == 0:
                    continue
                # for every term of the query
                for term in query_terms:
                    # tf_1 = fields_weight_dict[field] * self._tf_field(term, field, length_field[doc_id][field])
                    tf = fields_weight_dict[field] * tf_c[term][doc_id][field]
                    # if term do not exist in this field of document, we don't have to compute score...
                    if tf == 0:
                        continue
                    # idf = self._idf(term)     // --> almost got half time with that change
                    temp_score += idf[term] * (
                                                (tf * (k1 + 1)) /
                                                (
                                                    tf + (
                                                        k1 * (
                                                            1 - b + b * (
                                                                length_field[str(doc_id)][str(field)] /
                                                                avg_lf[str(field)]
                                                            )
                                                        )
                                                    )
                                                ))

            score[doc_id] = temp_score

        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (BM25F search):", time_diff, "seconds")
        start_time = time.time()
        sorted_scores = sorted(score.items(), key=lambda x: x[1], reverse=True)
        end_time = time.time()
        time_diff = end_time - start_time
        print("Sorting (BM25F search):", time_diff, "seconds")
        return [doc_id for doc_id, score in sorted_scores]

    def _idf_calculation(self, query_terms):
        idf_dict = defaultdict(float)
        for word in query_terms:
            unique_docs = self._number_of_word_docs(word)
            # return math.log(((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5)) + 1)
            if unique_docs != 0:
                idf_dict[word] = math.log(self.total_docs / unique_docs)
            else:
                idf_dict[word] = 0
        return idf_dict

    def _idf(self, word):
        unique_docs = self._number_of_word_docs(word)
        # return math.log(((self.total_docs - unique_docs + 0.5) / (unique_docs + 0.5)) + 1)
        return math.log(self.total_docs / unique_docs)

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
