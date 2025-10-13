from networksecurity.component.data_ingestion_component import DataIngestion
from networksecurity.component.data_validation import DataValidation
from networksecurity.component.data_transformation import DataTransformation
from networksecurity.component.model_trainer import ModelTrainer


from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import (
    DataIngestionConfig,
    DataValidationConfig,
    TrainingPipelineConfig,
    DataTransformationConfig,
    ModelTrainerConfig
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

        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        logging.info("Data Transformation Initiated")
        data_transformation=DataTransformation(data_validation_artifact=data_validation_artifact,
                           data_transformation_config=data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data Transformation Completed")

        logging.info("Starting model training...")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()
        logging.info("Model Trainer artifact created")

    except Exception as e:
        raise NetworkSecurityException(e, sys)