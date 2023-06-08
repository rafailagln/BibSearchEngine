import random
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec
from gensim.models.phrases import Phraser

# Load pre-trained Word2Vec model.
model = Word2Vec.load("word2vec.model")
def preprocess_data(input_phrase):
    # Lowercase the phrase and tokenize it
    processed_phrase = word_tokenize(input_phrase.lower())
    # Load phrases model
    phrases_model = Phraser.load('phrases_model.txt')
    # Apply phrases model to the tokenized phrase
    processed_phrase = phrases_model[processed_phrase]
    return processed_phrase
def generate_alternative_sentences(input_phrase, num_sentences=5, topn=5):
    # Preprocess the input_phrase
    processed_input = preprocess_data(input_phrase)

    # Get the most similar words for each word in the input_phrase
    similar_words = {word: [item[0] for item in model.wv.most_similar(word, topn=topn)] for word in processed_input if word in model.wv}

    # Generate new sentences
    new_sentences = set()
    attempts = 0
    max_attempts = num_sentences * 10  # Arbitrary number of maximum attempts

    while len(new_sentences) < num_sentences and attempts < max_attempts:
        for i in range(topn):  # Iterate over topn most similar words
            new_sentence = []
            for word in processed_input:
                # Select the ith most similar word if it exists in the similar_words dict, else use the original word
                new_word = similar_words.get(word, [word])[i % len(similar_words.get(word, [word]))]  # Use modulo to prevent index errors
                new_sentence.append(new_word)
            new_sentences.add(' '.join(new_sentence))
            attempts += 1
            if len(new_sentences) >= num_sentences:
                break  # Exit if we have enough sentences

    return [sentence.replace('_', ' ') for sentence in new_sentences]

# def generate_phrases_from_list(phrases_list):
#     separated_output = [phrase.replace('_', ' ') for phrase in phrases_list]
#
#     for phrase in separated_output:
#         print(phrase)
#
#     # If you want the function to return the phrases instead of printing them, use the following:
#     return separated_output



