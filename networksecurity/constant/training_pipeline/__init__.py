import os


PIPELINE_NAME = "networksecurity"
ARTIFACT_DIR = "artifact"
FILE_NAME = "PhishingData.csv"

TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"

DATA_INGESTION_COLLECTION_NAME = "Network_Data"
DATA_INGESTION_DATABASE_NAME = "CyverSecurity"
DATA_INGESTION_DIR_NAME = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR = "feature_store"
DATA_INGESTION_INGESTED_DIR = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION = 0.2

TARGET_COLUMN = "result"

SCHEMA_FILE_PATH = os.path.join("data_schema","schema.yaml")


DATA_VALIDATION_DIR_NAME:str= "data_validation"
DATA_VALIDATION_VALID_DIR = "validated"
DATA_VALIDATION_INVALID_DIR = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME = "report.yaml"