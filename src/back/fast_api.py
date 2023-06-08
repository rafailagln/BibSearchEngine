import time
import uvicorn
import concurrent.futures

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List

from configurations.read_config import IniConfig
from distributed.config_manager import ConfigManager
from distributed.request_wrapper import RequestWrapper
from logger import MyLogger

logger = MyLogger()

app = FastAPI()
security = HTTPBasic()
config_manager = ConfigManager("./config.json")
request_wrapper = RequestWrapper("./config.json")
ini_config = IniConfig('./config.ini')

# Add the following middleware to add the Access-Control-Allow-Origin header
origins = [
    ini_config.get_property('API', 'origin1'),
    ini_config.get_property('API', 'origin2'),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Validates the provided username and password against the configured credentials.

    Args:
        credentials: The HTTP basic authentication credentials.

    Returns:
        The username if the credentials are correct.

    Raises:
        HTTPException with status code 401 if the credentials are incorrect.
    """
    correct_username = ini_config.get_property('API', 'username')
    correct_password = ini_config.get_property('API', 'password')
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get('/search_ids/{query}', response_model=List[int])
def search_ids(query: str):
    """
    Retrieves a list of document IDs matching the provided query.

    Args:
        query: The search query.

    Returns:
        A list of document IDs as the search result.
    """
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(request_wrapper.search_ids, query)
    ids = future.result()
    logger.log_info(f"Returned {len(ids['results'])} document IDs")
    end_time = time.time()
    logger.log_info(f"Elapsed time: {end_time - start_time}")
    return ids['results']


@app.get("/alternate_queries/{query}", response_model=List[str])
def alternate_queries(query: str):
    """
    Retrieves a list of alternate queries based on the provided query.

    Args:
        query: The original query.

    Returns:
        A list of alternate queries.
    """
    return ['test1', 'test2', 'test3', 'test4', 'test5']


@app.post('/fetch_data/', response_model=List[dict])
def fetch_data(ids: List[int]):
    """
    Fetches data for the specified document IDs.

    Args:
        ids: A list of document IDs.

    Returns:
        A list of dictionaries containing the fetched data for each document.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(request_wrapper.fetch_data, ids)
    results = future.result()
    logger.log_info(f"Fetched data for {len(results['results'])} documents")
    return results['results']


@app.post("/update_config")
async def read_protected_endpoint(request: Request, _: str = Depends(get_current_username)):
    """
    Updates the configuration and saves it.

    Args:
        _: Used to validate the credentials.
        request: The HTTP request containing the updated configuration data.

    Returns:
        A JSON response with the status "OK" after updating the configuration.
    """
    data = await request.json()
    config_manager.save_config(data)
    request_wrapper.neighbour_nodes = data
    return {'status': 'OK'}


if __name__ == "__main__":
    uvicorn.run(app, host=ini_config.get_property('API', 'host'), port=int(ini_config.get_property('API', 'port')))
