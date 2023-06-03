import re
import math
from collections import Counter


class Relevancy:

    @staticmethod
    def cosine_similarity(s1, s2):
        """
        Calculates the cosine similarity between two sentences.

        Inputs:
        - s1: The first sentence (string)
        - s2: The second sentence (string)

        Output:
        - similarity: The cosine similarity between the two sentences (float)
        """
        # Tokenize the sentences
        words1 = re.findall('\\w+', s1.lower())
        words2 = re.findall('\\w+', s2.lower())

        # Calculate the term frequencies
        tf1 = Counter(words1)
        tf2 = Counter(words2)

        # Get the set of unique words in both sentences
        all_words = set(words1).union(set(words2))

        # Calculate the dot product of the term frequencies
        dot_product = sum(tf1.get(word, 0) * tf2.get(word, 0) for word in all_words)

        # Calculate the magnitude of each sentence vector
        mag1 = math.sqrt(sum(tf1.get(word, 0) ** 2 for word in all_words))
        mag2 = math.sqrt(sum(tf2.get(word, 0) ** 2 for word in all_words))

        # Calculate the cosine similarity
        if mag1 == 0 or mag2 == 0:
            return 0
        else:
            return dot_product / (mag1 * mag2)
