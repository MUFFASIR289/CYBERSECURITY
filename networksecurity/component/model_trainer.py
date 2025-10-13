import os
import sys
import mlflow

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import evaluate_model, save_object, load_object, load_numpy_array_data
from networksecurity.utils.m1_utils.model.estimator import NetworkModel
from networksecurity.utils.m1_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def train_model(self, x_train, y_train, x_test, y_test):
        models = {
            "LogisticRegression": LogisticRegression(verbose=1),
            "KNeighborsClassifier": KNeighborsClassifier(),
            "DecisionTreeClassifier": DecisionTreeClassifier(),
            "RandomForestClassifier": RandomForestClassifier(verbose=1),
            "AdaBoostClassifier": AdaBoostClassifier(),
            "GradientBoostingClassifier": GradientBoostingClassifier(verbose=1)
        }

        params = {
            "LogisticRegression": {},
            "KNeighborsClassifier": {
                'n_neighbors': [5, 10],
                'weights': ['uniform', 'distance'],
                'algorithm': ['auto'],
                'p': [1, 2]
            },
            "DecisionTreeClassifier": {
                'criterion': ['gini', 'entropy'],
                'max_depth': [5, 10],
                'splitter': ['best'],
                'max_features': ['sqrt']
            },
            "RandomForestClassifier": {
                'n_estimators': [64, 128],
                'criterion': ['gini'],
                'max_depth': [10, 20]
            },
            "AdaBoostClassifier": {
                'n_estimators': [64, 128],
                'learning_rate': [0.5, 1.0],
                'algorithm': ['SAMME']  # ✅ Fixed here
            },
            "GradientBoostingClassifier": {
                'n_estimators': [64, 128],
                'learning_rate': [0.5, 1.0],
                'loss': ['log_loss'],
                'subsample': [0.8, 1.0]
            }
        }

        model_report = evaluate_model(x_train, y_train, x_test, y_test, models, params)

        if not model_report:
            raise NetworkSecurityException("No model was successfully trained or evaluated.", sys)

        best_model_score = max(model_report.values())
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
        best_model = models[best_model_name]

        logging.info(f"✅ Best model selected: {best_model_name} with score: {best_model_score}")

        if best_model_score < self.model_trainer_config.expected_accuracy:
            raise NetworkSecurityException(
                f"Model accuracy {best_model_score} is below expected threshold {self.model_trainer_config.expected_accuracy}",
                sys
            )

        y_train_pred = best_model.predict(x_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        y_test_pred = best_model.predict(x_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        # ✅ MLflow setup for local tracking
        os.environ["MLFLOW_ENABLE_ARTIFACTS_LOGGING"] = "false"
        mlflow.set_tracking_uri("file:///mlruns")

        with mlflow.start_run(run_name=best_model_name):
            mlflow.log_param("model_name", best_model_name)
            mlflow.log_params(params[best_model_name])
            mlflow.log_metric("f1_score", classification_test_metric.f1_score)
            mlflow.log_metric("precision", classification_test_metric.precision_score)
            mlflow.log_metric("recall", classification_test_metric.recall_score)
            mlflow.set_tag("pipeline_stage", "model_training")
            mlflow.log_model(best_model, artifact_path="model")  # ✅ safer for local use

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=network_model)

        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )

        logging.info(f"✅ Model Trainer Artifact: {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            x_train = train_arr[:, :-1]
            y_train = train_arr[:, -1]

            x_test = test_arr[:, :-1]
            y_test = test_arr[:, -1]

            return self.train_model(x_train, y_train, x_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)