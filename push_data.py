import os
import sys
import json

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(f"MongoDB URL: {MONGO_DB_URL}")

import certifi
ca = certifi.where()

import pandas as pd
import numpy as np
import pymongo

from networksecurity.logging.logger import logger
from networksecurity.exception.exception import NetworkSecurityException


class NetworkDataExtract:

    def __init__(self):
        try:
            # You can initialize shared resources here if needed
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(inplace=True, drop=True)
            records = list(json.loads(data.T.to_json()).values())
            logger.info(f"Converted {len(records)} records from CSV to JSON")
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            # ✅ Initialize MongoDB client with SSL certificate
            mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)

            # ✅ Get database and collection objects
            db = mongo_client[database]
            coll = db[collection]

            # ✅ Insert records
            result = coll.insert_many(records)
            logger.info(f"Inserted {len(result.inserted_ids)} records into {database}.{collection}")
            return len(result.inserted_ids)
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == '__main__':
    try:
        FILE_PATH = "Network_Data/PhishingData.csv"  # ✅ Use forward slash for cross-platform compatibility
        DATABASE = "CyberSecurity"
        COLLECTION = "NetworkData"

        networkobj = NetworkDataExtract()
        records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)
        print(f"Sample record: {records[0] if records else 'No records found'}")

        no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
        print(f"✅ Number of records inserted: {no_of_records}")
    except Exception as e:
        print(f"❌ Failed to insert data: {e}")