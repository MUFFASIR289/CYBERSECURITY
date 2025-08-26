from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH

from scipy.stats import ks_2samp
import pandas as pd
import os
import sys

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(r"[^\w]", "", regex=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = list(self._schema_config["columns"].keys())
            actual_columns = dataframe.columns.tolist()

            logging.info(f"Expected number of columns: {len(expected_columns)}")
            logging.info(f"Actual number of columns: {len(actual_columns)}")

            print("📋 Expected columns:", expected_columns)
            print("📄 Actual columns:", actual_columns)

            missing = set(expected_columns) - set(actual_columns)
            extra = set(actual_columns) - set(expected_columns)

            if missing or extra:
                print("❌ Missing columns:", missing)
                print("⚠️ Extra columns:", extra)

            return len(actual_columns) == len(expected_columns)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_dataset_drift(self, base_df: pd.DataFrame, current_df: pd.DataFrame, threshold=0.05) -> bool:
        try:
            status = True
            report = {}

            for column in base_df.columns:
                if column not in current_df.columns:
                    report[column] = {
                        "p_value": None,
                        "drift_status": "Column missing in test set"
                    }
                    status = False
                    continue

                d1 = base_df[column].dropna()
                d2 = current_df[column].dropna()

                if d1.empty or d2.empty:
                    report[column] = {
                        "p_value": None,
                        "drift_status": "Insufficient data for comparison"
                    }
                    continue

                test_result = ks_2samp(d1, d2)
                drift_detected = test_result.pvalue < threshold

                report[column] = {
                    "p_value": float(test_result.pvalue),
                    "drift_status": drift_detected
                }

                if drift_detected:
                    status = False

            report["summary"] = {
                "drift_detected": not status,
                "threshold": threshold
            }

            logging.info(f"📊 Drift report content: {report}")

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            os.makedirs(os.path.dirname(drift_report_file_path), exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)

            logging.info(f"📊 Drift report saved to: {drift_report_file_path}")
            return status
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_df = self.read_data(train_file_path)
            test_df = self.read_data(test_file_path)

            if not self.validate_number_of_columns(train_df):
                raise NetworkSecurityException("Train dataframe has incorrect number of columns", sys)

            if not self.validate_number_of_columns(test_df):
                raise NetworkSecurityException("Test dataframe has incorrect number of columns", sys)

            validation_status = self.detect_dataset_drift(train_df, test_df)

            os.makedirs(os.path.dirname(self.data_validation_config.valid_train_file_path), exist_ok=True)

            train_df.to_csv(self.data_validation_config.valid_train_file_path, index=False, header=True)
            test_df.to_csv(self.data_validation_config.valid_test_file_path, index=False, header=True)

            logging.info(f"✅ Validated train.csv saved to: {self.data_validation_config.valid_train_file_path}")
            logging.info(f"✅ Validated test.csv saved to: {self.data_validation_config.valid_test_file_path}")

            return DataValidationArtifact(
                validation_status=validation_status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

        except Exception as e:
            raise NetworkSecurityException(e, sys)