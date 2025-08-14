import pandas as pd
import pymongo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_DB_URL"))
db = client["CyverSecurity"]
collection = db["Network_Data"]

# Load your CSV file
csv_path = "Network_Data/PhishingData.csv"  # Adjust path if needed
df = pd.read_csv(csv_path)

# Push data to MongoDB
collection.insert_many(df.to_dict(orient="records"))
print(f"✅ Inserted {len(df)} records into MongoDB.")