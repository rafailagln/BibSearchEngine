import logging
import time
import uvicorn
import concurrent.futures
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from distributed.request_wrapper import search_ids_wrapper, fetch_data_wrapper

# TODO: add search_ids and fetch_data in new thread to have non-blocking actions
# TODO: convert FastAPI to accept request from frond, forward to node, get results
#       and then fetch results in buckets


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Add the following middleware to add the Access-Control-Allow-Origin header
origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: add error page
# TODO: if a server crash not fail all the system
# TODO: check if using only multithreading in search_ids is better than using threads at multiple points of code


@app.get('/search_ids/{query}', response_model=List[int])
def search_ids(query: str):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(search_ids_wrapper, query)
    ids = future.result()
    logging.info(f"Returned {len(ids)} document IDs")
    end_time = time.time()
    logging.info(f"Elapsed time: {end_time - start_time}")
    return ids


@app.post('/fetch_data/', response_model=List[dict])
def fetch_data(ids: List[int]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(fetch_data_wrapper, ids)
    results = future.result()
    logging.info(f"Fetched data for {len(results['results'])} documents")
    return results['results']


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
