from pymongo import MongoClient

client = MongoClient(
    "mongodb://127.0.0.1:27017/",
    serverSelectionTimeoutMS=5000
)

client.admin.command("ping")

db = client["LoginDB"]
users = db["Users"]

print("MongoDB connection successful")
print("Database:", db.name)
print("Collection:", users.name)
print("Document count:", users.count_documents({}))

for user in users.find({}, {"_id": 0, "password": 0}):
    print(user)

client.close()
