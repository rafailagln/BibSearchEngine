from multiprocessing import Pool, cpu_count
from collections import defaultdict
import numpy as np
import time

from ranker import BM25F


class BM25FParallel(BM25F):
    def __init__(self, inverted_index, total_docs):
        super().__init__(inverted_index, total_docs)
        self.pool = Pool(cpu_count())

    @staticmethod
    def _score_documents(docs_chunk, query_terms, fields_weight_dict, length_field, avg_lf, idf, tf_c,
                         algorithm_parameters):
        score = defaultdict(float)
        for doc_id in docs_chunk:
            temp_score = 0.0
            for field in fields_weight_dict:
                if length_field[str(doc_id)][str(field)] == 0:
                    continue
                factor = algorithm_parameters[field]["k1"] * (1 - algorithm_parameters[field]["b"] +
                                                              algorithm_parameters[field]["b"] *
                                                              (length_field[str(doc_id)][str(field)] /
                                                               avg_lf[str(field)]))
                for term in query_terms:
                    tf = fields_weight_dict[field] * tf_c[term][doc_id][field]
                    if tf == 0:
                        continue
                    temp_score += idf[term] * ((tf * (algorithm_parameters[field]["k1"] + 1)) / (tf + factor))

            score[doc_id] = temp_score
        return score

    def bm25f(self, docs, query_terms, fields_weight_dict, length_field, avg_lf):
        score = defaultdict(float)
        start_time = time.time()
        idf = self._idf_calculation(query_terms)
        tf_c = self._tf_field_calculation(query_terms)
        algorithm_parameters = self._algorith_parameters()

        docs_chunks = np.array_split(docs, 1)
        results = self.pool.starmap(self._score_documents, [
            (chunk, query_terms, fields_weight_dict, length_field, avg_lf, idf, tf_c, algorithm_parameters) for chunk in
            docs_chunks])

        for result in results:
            score.update(result)

        end_time = time.time()
        time_diff = end_time - start_time
        print("Time elapsed (BM25F search):", time_diff, "seconds")

        return score

