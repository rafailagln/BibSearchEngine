import os
import pymongo
import json
from Basics.connection2 import MongoDBConnection

with MongoDBConnection() as conn:
    mongo = conn.get_connection()
    papers_big = mongo.get_database('M151Dev').get_collection('Papers_big')
    papers_big_lookup = mongo.get_database('M151Dev').get_collection('Papers_big_lookup')

    json_dir_path = "/path/to/folder/"

    total_files = len([f for f in os.listdir(json_dir_path) if f.endswith(".json")])

    for index, filename in enumerate(os.listdir(json_dir_path)):
        if filename.endswith(".json"):
            if papers_big_lookup.count_documents({"filename": filename[:-5]}) == 0:
                print(f"Inserting {filename}... ", end="")

                with open(os.path.join(json_dir_path, filename)) as f:
                    json_data = f.read()

                # Convert the json to a list of dictionary objects
                json_list = json.loads(json_data)

                papers_big.insert_many(json_list)
                papers_big_lookup.insert_one({"filename": filename[:-5]})

                print(f"Done! Inserted {len(json_list)} documents from {filename} ", end="")
            else:
                print(f"Skipping {filename}, already inserted into Papers_big collection ", end="")

            percent = (index + 1) / total_files * 100
            print(f"({percent:.2f}% complete)")
