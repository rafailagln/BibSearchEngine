import pymongo

# Connect to the MongoDB server˜
connectionString = 'mongodb+srv://notaris:YyKOhV1xa3mnmlFP@m151cluster.lsdswbf.mongodb.net'

client = pymongo.MongoClient(connectionString)

# Get the "assignment" database
db = client["M151"]

# Get the "Papers" collection
collection = db["Papers"]

results = collection.find()

print(list(results))
