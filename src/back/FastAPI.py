import logging
import uvicorn
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
# from Ranker.Search1 import SearchEngine
from Ranker.Search2 import SearchEngine
from Data.FastJsonLoader import FastJsonLoader, read_config_file

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

start_time = time.time()
documents_per_file = read_config_file('config.ini')
db = FastJsonLoader('/home/notaris/data/', documents_per_file)
db.load_documents()
end_time = time.time()
time_diff = end_time - start_time
logging.info(f"Time to load to memory: {time_diff} seconds")

engine = SearchEngine(db, max_results=10000)

# Add the following middleware to add the Access-Control-Allow-Origin header
origins = [
    # "http://localhost",
    "http://vmi1224404.contaboserver.net:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/search_ids/{query}', response_model=List[int])
def search_ids(query: str):
    ids = engine.search_ids(query)
    logging.info(f"Returned {len(ids)} document IDs")
    return ids


@app.post('/fetch_data/', response_model=List[dict])
def fetch_data(ids: List[int]):
    results = engine.fetch_data(ids)
    logging.info(f"Fetched data for {len(results)} documents")
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
