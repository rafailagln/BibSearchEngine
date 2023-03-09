from flask import Flask, jsonify
import random

app = Flask(__name__)

BASE_URL = "https://example.com/articles"


def generate_result():
    article_num = random.randint(1, 1000)
    title = f"Article {article_num}"
    url = f"{BASE_URL}/{article_num}"
    snippet = f"Lorem ipsum dolor sit amet, consectetur adipiscing elit, " \
              f"sed do eiusmod tempor incididunt ut labore et dolore magna " \
              f"aliqua. Nulla aliquet porttitor lacus luctus accumsan tortor " \
              f"posuere. Et odio pellentesque diam volutpat commodo sed egestas. " \
              f"Sed tempus urna et pharetra."
    return {"title": title, "url": url, "snippet": snippet}


@app.route('/search/<query>', methods=['GET'])
def search(query):
    results = [generate_result() for _ in range(100)]
    random.shuffle(results)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
