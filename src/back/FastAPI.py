import logging
import time
import uvicorn
import concurrent.futures

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List

from distributed.config_manager import ConfigManager
from distributed.request_wrapper import RequestWrapper

# TODO: add search_ids and fetch_data in new thread to have non-blocking actions
# TODO: convert FastAPI to accept request from frond, forward to node, get results
#       and then fetch results in buckets


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()
security = HTTPBasic()
config_manager = ConfigManager("/Users/notaris/git/BibSearchEngine/src/back/config.json")
request_wrapper = RequestWrapper("/Users/notaris/git/BibSearchEngine/src/back/config.json")

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

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "testuser"
    correct_password = "testpass"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get('/search_ids/{query}', response_model=List[int])
def search_ids(query: str):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(request_wrapper.search_ids, query)
    ids = future.result()
    logging.info(f"Returned {len(ids['results'])} document IDs")
    end_time = time.time()
    logging.info(f"Elapsed time: {end_time - start_time}")
    return ids['results']


@app.post('/fetch_data/', response_model=List[dict])
def fetch_data(ids: List[int]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(request_wrapper.fetch_data, ids)
    results = future.result()
    logging.info(f"Fetched data for {len(results['results'])} documents")
    return results['results']


@app.post("/update_config")
async def read_protected_endpoint(request: Request, username: str = Depends(get_current_username)):
    data = await request.json()
    config_manager.save_config(data)
    request_wrapper.neighbour_nodes = data
    return {'status': 'OK'}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
