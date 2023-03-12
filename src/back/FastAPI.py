from fastapi import FastAPI
from typing import List
from random import randint, shuffle
import uvicorn

app = FastAPI()

BASE_URL = "https://example.com/articles"


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
    return {"title": title, "url": url, "snippet": snippet}


@app.get('/search/{query}', response_model=List[dict])
def search(query: str):
    results = [generate_result() for _ in range(100)]
    shuffle(results)
    return results

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
