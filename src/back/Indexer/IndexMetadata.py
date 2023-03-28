import sys
from collections import defaultdict


class Metadata:

    def __init__(self):
        self.length_field = defaultdict(lambda: defaultdict(int))
        self.average_length = defaultdict(float)
        self.total_docs = 0

    def update_doc_num(self):
        self.total_docs += 1

    def add_doc_length_field(self, doc_id, length, field):
        self.length_field[doc_id][field] = length

    def increase_average_length(self, length, field):
        self.average_length[field] += length

    def calculate_average_length(self):
        for field in self.average_length.keys():
            self.average_length[field] /= self.total_docs

    def load(self, metadata_collection):
        print("HAVE TO IMPLEMENT LOAD FOR METADATA")
        sys.exit(1)
        pass
