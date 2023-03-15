import logging
import time

from fastapi import FastAPI
from typing import List
from random import randint
import uvicorn
from Ranker.Rank import Rank


start_time = time.time()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
BASE_URL = "https://example.com/articles"
rank = Rank()
end_time = time.time()
time_diff = end_time - start_time
logging.info(f"Time to start API: {time_diff} seconds")


def generate_result():
    article_num = randint(1, 1000)
    title = f"Article {article_num}"
    url = f"{BASE_URL}/{article_num}"
    snippet = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna "
        "aliqua. Nulla aliquet porttitor lacus luctus accumsan tortor "
        "posuere. Et odio pellentesque diam volutpat commodo sed egestas. "
        "Sed tempus urna et pharetra."
    )
    return {"title": title, "URL": url, "abstract": snippet}


@app.get('/search/{query}', response_model=List[dict])
def search(query: str):
    # results = [generate_result() for _ in range(100)]
    # shuffle(results)
    return rank.final_results(query)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
