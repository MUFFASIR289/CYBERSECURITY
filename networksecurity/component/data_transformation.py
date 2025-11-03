import sys
import os
import numpy as np
import pandas as pd

from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN, DATA_TRANSFORMATION_IMPUTER_PARAMS
from networksecurity.entity.artifact_entity import DataTransformationArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        try:
            self.data_validation_artifact = data_validation_artifact
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def get_data_transformer_object(self) -> Pipeline:
        try:
            logging.info("Entered get_data_transformer_object method of DataTransformation class")
            imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"Initialized KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}")
            preprocessor = Pipeline(steps=[('imputer', imputer)])
            return preprocessor
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation method of DataTransformation class")
        try:
            logging.info("Starting data transformation")

            train_df = self.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = self.read_data(self.data_validation_artifact.valid_test_file_path)

            # Training dataframe
            input_feature_train_data = train_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_train_data = train_df[TARGET_COLUMN]

            # Replace -1 with 0 only if -1 exists
            if -1 in target_feature_train_data.unique():
                target_feature_train_data = target_feature_train_data.replace(-1, 0)

            # Testing dataframe
            input_feature_test_data = test_df.drop(columns=[TARGET_COLUMN], axis=1)
            target_feature_test_data = test_df[TARGET_COLUMN]

            if -1 in target_feature_test_data.unique():
                target_feature_test_data = target_feature_test_data.replace(-1, 0)

            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_data)

            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_data)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_data)

            train_arr = np.c_[transformed_input_train_feature, np.array(target_feature_train_data)]
            test_arr = np.c_[transformed_input_test_feature, np.array(target_feature_test_data)]

            # Save numpy array data
            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path, train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path, test_arr)

            # Save preprocessor object
            save_object(self.data_transformation_config.transformed_object_file_path, preprocessor_object)

            save_object('final_model/preprocessor.pkl',preprocessor_object)

            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path
            )

            logging.info(f"✅ Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)