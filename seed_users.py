from pymongo import MongoClient, ASCENDING
from werkzeug.security import generate_password_hash
import os

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["LoginDB"]
users = db["Users"]

users.create_index([("username", ASCENDING)], unique=True)

users.delete_many({})

sample_users = [
    {
        "name": "Rahul Sharma",
        "username": "rahul1123",
        "password": "Rahul@123",
        "age": 21,
        "department": "CSE",
        "skills": ["Python", "MongoDB"],
        "address": {"city": "Ghaziabad", "state": "Uttar Pradesh"}
    },
    {
        "name": "Priya Verma",
        "username": "priya2026",
        "password": "Priya@123",
        "age": 22,
        "department": "IT",
        "skills": ["Java", "MongoDB"],
        "address": {"city": "Delhi", "state": "Delhi"}
    },
    {
        "name": "Amit Kumar",
        "username": "amit2026",
        "password": "Amit@123",
        "age": 20,
        "department": "IT",
        "skills": ["Python", "SQL"],
        "address": {"city": "Meerut", "state": "Uttar Pradesh"}
    },
    {
        "name": "Neha Singh",
        "username": "neha2026",
        "password": "Neha@123",
        "age": 23,
        "department": "CSE",
        "skills": ["MongoDB", "JavaScript"],
        "address": {"city": "Ghaziabad", "state": "Uttar Pradesh"}
    },
    {
        "name": "Vikas Gupta",
        "username": "vikas2026",
        "password": "Vikas@123",
        "age": 22,
        "department": "IT",
        "skills": ["Python", "SQL"],
        "address": {"city": "Noida", "state": "Uttar Pradesh"}
    },
    {
        "name": "Anjali Mishra",
        "username": "anjali2026",
        "password": "Anjali@123",
        "age": 21,
        "department": "CSE",
        "skills": ["Python", "MongoDB", "AI"],
        "address": {"city": "Delhi", "state": "Delhi"}
    }
]

for user in sample_users:
    user["password"] = generate_password_hash(user["password"])

result = users.insert_many(sample_users)

print("MongoDB connection successful.")
print("Database:", db.name)
print("Collection:", users.name)
print("Inserted documents:", len(result.inserted_ids))
print("Total documents:", users.count_documents({}))

for user in users.find({}, {"_id": 0, "password": 0}).sort("username", 1):
    print(user)

client.close()
