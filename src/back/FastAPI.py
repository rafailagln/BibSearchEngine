import logging
import time

from fastapi import FastAPI
from typing import List
import uvicorn
from Ranker.Search import SearchEngine
from Data.FastJsonLoader import FastJsonLoader

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

start_time = time.time()
db = FastJsonLoader('/path/to/data/')
db.load_documents()
end_time = time.time()
time_diff = end_time - start_time
logging.info(f"Time to load to memory: {time_diff} seconds")

engine = SearchEngine(db, max_results=10000)


@app.get('/search/{query}', response_model=List[dict])
def search(query: str):
    return engine.final_results(query)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
