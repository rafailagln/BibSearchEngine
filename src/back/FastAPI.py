import logging
import uvicorn
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


# TODO: make wrapper function to not call engine and send-receive results like the function
#  "def send_request_wrapper(node)" in "def execute_action()"

@app.get('/search_ids/{query}', response_model=List[int])
def search_ids(query: str):
    ids = search_ids_wrapper(query)
    logging.info(f"Returned {len(ids)} document IDs")
    return ids


@app.post('/fetch_data/', response_model=List[dict])
def fetch_data(ids: List[int]):
    results = fetch_data_wrapper(ids)
    logging.info(f"Fetched data for {len(results)} documents")
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
