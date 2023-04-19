import random
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec


# Load pre-trained Word2Vec model.
model = Word2Vec.load("word2vec.model")
def preprocess_data(input_phrase):
    # Lowercase the phrase and tokenize it
    processed_phrase = word_tokenize(input_phrase.lower())
    return processed_phrase

def generate_alternative_sentences(input_phrase, num_sentences=5):
    # Preprocess the input_phrase
    processed_input = preprocess_data(input_phrase)

    # Get the most similar words for each word in the input_phrase
    similar_words = {word: [item[0] for item in model.wv.most_similar(word, topn=5)] for word in processed_input if word in model.wv}

    # Generate new sentences
    new_sentences = []
    for _ in range(num_sentences):
        new_sentence = []
        for word in processed_input:
            # Randomly select a similar word if it exists in the similar_words dict, else use the original word
            new_word = random.choice(similar_words.get(word, [word]))
            new_sentence.append(new_word)
        new_sentences.append(' '.join(new_sentence))

    return [new_sentences.replace('_', ' ') for phrase in new_sentences]

# def generate_phrases_from_list(phrases_list):
#     separated_output = [phrase.replace('_', ' ') for phrase in phrases_list]
#
#     for phrase in separated_output:
#         print(phrase)
#
#     # If you want the function to return the phrases instead of printing them, use the following:
#     return separated_output



