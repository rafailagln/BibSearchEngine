import logging
import time

from fastapi import FastAPI
from typing import List
import uvicorn
# from Ranker.Rank import SearchEngine
from Ranker.Search2 import SearchEngine
from Data.FastJsonLoader import FastJsonLoader, read_config_file

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

start_time = time.time()
documents_per_file = read_config_file('config.ini')
db = FastJsonLoader('/path/to/data/', documents_per_file)
db.load_documents()
end_time = time.time()
time_diff = end_time - start_time
logging.info(f"Time to load to memory: {time_diff} seconds")

engine = SearchEngine(db, max_results=10000)


@app.get('/search/{query}', response_model=List[dict])
def search(query: str):
    results = engine.final_results(query)
    logging.info(f"Returned {len(results)} documents")
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
