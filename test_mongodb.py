from pymongo import MongoClient
import os

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["LoginDB"]
users = db["Users"]

print("MongoDB connection successful")
print("Server:", client.server_info()["version"])
print("Database:", db.name)
print("Collection:", users.name)
print("Document count:", users.count_documents({}))

for user in users.find({}, {"_id": 0, "password": 0}).sort("username", 1):
    print(user)

client.close()
