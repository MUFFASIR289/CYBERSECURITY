from pymongo import MongoClient

# Use your actual MongoDB connection string
client = MongoClient("mongodb://localhost:27017")

# Access the correct database and collection
db = client["CyberSecurity"]
collection = db["NetworkData"]

# Count and print documents
count = collection.count_documents({})
print("📊 Document count:", count)

# Optionally preview a few documents
docs = list(collection.find().limit(3))
for i, doc in enumerate(docs):
    print(f"📄 Document {i+1}:", doc)