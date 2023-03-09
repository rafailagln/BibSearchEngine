import pymongo

# Connect to the MongoDB server˜
connectionString = 'mongodb://localhost:27017'

client = pymongo.MongoClient(connectionString)

# Get the "assignment" database
db = client["M151"]

# Get the "Papers" collection
collection = db["Papers_small"]

results = collection.find()

print(list(results))
