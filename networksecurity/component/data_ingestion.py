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

            # Connect to MongoDB
            client = MongoClient(MONGO_DB_URL)
            collection = client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            logging.info(f"✅ Fetched {len(df)} records from MongoDB")

            # Drop MongoDB internal ID
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            # Rename malformed fields first
            rename_map = {
                "having_IPhaving_IP_Address ": "having_IP_Address",
                "URLURL_Length ": "URL_Length",
                "Domain_registeration_length ": "Domain_Registeration_Length"
            }
            df.rename(columns=rename_map, inplace=True)

            # Drop unwanted and malformed columns
            drop_columns = [
                "index ", "having_Sub_Domain ",
                "having_IPhaving_IP_Address ", "URLURL_Length ", "Domain_registeration_length "
            ]
            for col in drop_columns:
                if col in df.columns:
                    df.drop(columns=[col], inplace=True)
                    logging.warning(f"⚠️ Dropped malformed column: {col}")

            # Clean column names
            df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)

            # Ensure required columns exist
            required_columns = [
                "having_IP_Address", "URL_Length", "Domain_Registeration_Length"
            ]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = np.nan
                    logging.warning(f"⚠️ Added missing column: {col} with NaN values")

            df.replace({"na": np.nan}, inplace=True)

            logging.info(f"📋 Final columns after cleaning: {df.columns.tolist()}")
            return df
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
            df = self.export_collection_as_dataframe()
            df = self.export_data_into_feature_store(df)
            train_set, test_set = self.split_data_as_train_test(df)

            return DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)