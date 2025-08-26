from networksecurity.component.data_ingestion import DataIngestion
from networksecurity.component.data_validation import DataValidation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    TrainingPipelineConfig
)

import sys

if __name__ == "__main__":
    try:
        # Initialize pipeline config
        training_pipeline_config = TrainingPipelineConfig()

        # Data Ingestion
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)

        logging.info("🚀 Initiating data ingestion process...")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("✅ Data Ingestion completed successfully.")
        print(data_ingestion_artifact)

        # Data Validation
        data_validation_config = DataValidationConfig(training_pipeline_config)

        # ✅ Pass the artifact, not the config
        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )

        logging.info("🔍 Initiating data validation process...")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("✅ Data Validation completed successfully.")
        print(data_validation_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)