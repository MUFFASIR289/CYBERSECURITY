from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import pandas as pd
import numpy as np
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import re

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            print("📁 Using database:", database_name)
            print("📂 Using collection:", collection_name)

            client = MongoClient(MONGO_DB_URL)
            collection = client[database_name][collection_name]

            docs = list(collection.find())
            print("📦 Sample documents:", docs[:2])
            raw_df = pd.DataFrame(docs)
            logging.info(f"✅ Fetched {len(raw_df)} records from MongoDB")

            if raw_df.empty:
                raise NetworkSecurityException("❌ No documents found in MongoDB collection", sys)

            if "_id" in raw_df.columns:
                raw_df.drop(columns=["_id"], inplace=True)

            logging.info(f"🧪 Raw column names before cleaning: {raw_df.columns.tolist()}")
            print("🧪 Raw columns from MongoDB:", raw_df.columns.tolist())

            # Clean column names
            cleaned_columns = [
                re.sub(r"[^\w]", "", str(col).strip().replace(" ", "_"))
                for col in raw_df.columns
            ]
            raw_df.columns = pd.Index(cleaned_columns)
            logging.info(f"🧼 Cleaned column names: {raw_df.columns.tolist()}")

            # Rename malformed fields
            rename_map = {
                "having_IPhaving_IP_Address": "having_IP_Address",
                "URLURL_Length": "URL_Length",
                "Domain_registeration_length": "Domain_Registeration_Length"
            }
            raw_df.rename(columns=rename_map, inplace=True)

            # Drop unwanted columns
            drop_columns = ["index", "having_Sub_Domain"]
            for col in drop_columns:
                if col in raw_df.columns:
                    raw_df.drop(columns=[col], inplace=True)
                    logging.warning(f"⚠️ Dropped extra column: {col}")

            # Ensure required columns exist
            required_columns = [
                "having_IP_Address", "URL_Length", "Domain_Registeration_Length"
            ]
            for col in required_columns:
                if col not in raw_df.columns:
                    raw_df[col] = np.nan
                    logging.warning(f"⚠️ Added missing column: {col} with NaN values")

            raw_df.replace({"na": np.nan}, inplace=True)

            logging.info(f"📊 Final DataFrame shape: {raw_df.shape}")
            logging.info(f"📋 Final columns after cleaning: {raw_df.columns.tolist()}")
            print(raw_df.head())

            if raw_df.empty:
                raise NetworkSecurityException("❌ DataFrame is empty after cleaning", sys)

            return raw_df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(os.path.dirname(feature_store_file_path), exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"✅ Saved feature store data to: {feature_store_file_path}")
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        try:
            if dataframe.empty:
                raise ValueError("DataFrame is empty. Cannot split.")

            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42
            )
            logging.info(f"📊 Train set shape: {train_set.shape}, Test set shape: {test_set.shape}")

            train_path = self.data_ingestion_config.training_file_path
            test_path = self.data_ingestion_config.testing_file_path

            os.makedirs(os.path.dirname(train_path), exist_ok=True)

            train_set.to_csv(train_path, index=False, header=True)
            test_set.to_csv(test_path, index=False, header=True)

            logging.info(f"✅ Saved train.csv to: {train_path}")
            logging.info(f"✅ Saved test.csv to: {test_path}")

            return train_set, test_set
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            print("✅ Running correct version of DataIngestion class")
            df = self.export_collection_as_dataframe()
            df = self.export_data_into_feature_store(df)
            train_set, test_set = self.split_data_as_train_test(df)

            return DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)