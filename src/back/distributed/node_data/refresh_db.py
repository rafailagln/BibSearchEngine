from pymongo import MongoClient

# MongoDB connection settings
host = "localhost"
port = 27017

# Database name to delete
db_name = "M151"

# Connect to MongoDB instance
client = MongoClient(host, port)

# Get the database
database = client[db_name]

# Print verbose information
print(f"Connected to MongoDB at {host}:{port}")
print(f"Deleting database: {db_name}")

# Delete the database
client.drop_database(db_name)

# Print verbose information
print("Database deletion completed.")

# Close the MongoDB connection
client.close()