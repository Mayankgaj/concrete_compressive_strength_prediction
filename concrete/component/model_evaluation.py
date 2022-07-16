from concrete.logger import logging
from concrete.exception import ConcreteException
from concrete.entity.config_entity import ModelEvaluationConfig
from concrete.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, ModelTrainerArtifact, \
    ModelEvaluationArtifact
from concrete.constant import *
import numpy as np
import os
import sys
from concrete.util.util import write_yaml_file, read_yaml_file, load_object, load_data
from concrete.entity.model_factory import evaluate_regression_model


class ModelEvaluation:

    def __init__(self, model_evaluation_config: ModelEvaluationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        """
        Description: Function is used to get data
                     Evaluation config to evaluate model
        param model_evaluation_config: model_evaluation_file_name: name of the model file
        param data_ingestion_artifact:author_username : username of the author
                                      kaggel_dataset_name : name of the dataset
                                      raw_data_dir: name of directory for download the dataset
                                      ingested_dir: name of directory where to split file
                                      ingested_train_dir: name of directory to save train file
                                      ingested_test_dir: name of directory to save test file
        param data_validation_artifact:directory name of schema file
                                       schema_file_name: name of schema file
                                       report_file_name: name of report of data drift
                                       report_page_file_name: name of the html file of report
        param model_trainer_artifact: is_trained: True if model is trained or False if not
                                      message: message after completing training model
                                      trained_model_file_path: Path of trained model
                                      train_rmse: rmse score of the trained file
                                      test_rmse: rmse score of the test file
                                      train_accuracy: accuracy of train file
                                      test_accuracy: accuracy of test file
                                      model_accuracy: accuracy of model
        """
        try:
            logging.info(f"{'>>' * 30}Model Evaluation log started.{'<<' * 30} ")
            self.model_evaluation_config = model_evaluation_config
            self.model_trainer_artifact = model_trainer_artifact
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def get_best_model(self):
        """
        Description: Function is used to get best model from model file
        return: model:model with best score
        """
        try:
            model = None
            model_evaluation_file_path = self.model_evaluation_config.model_evaluation_file_path

            if not os.path.exists(model_evaluation_file_path):
                write_yaml_file(file_path=model_evaluation_file_path,
                                )
                return model
            model_eval_file_content = read_yaml_file(file_path=model_evaluation_file_path)

            model_eval_file_content = dict() if model_eval_file_content is None else model_eval_file_content

            if BEST_MODEL_KEY not in model_eval_file_content:
                return model

            model = load_object(file_path=model_eval_file_content[BEST_MODEL_KEY][MODEL_PATH_KEY])
            return model
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def update_evaluation_report(self, model_evaluation_artifact: ModelEvaluationArtifact):
        """
        Description: Function write the best model in yml file
        param model_evaluation_artifact:is_model_accepted: True if model evaluated or False
                                        evaluated_model_path: Path to model config
        return: model file
        """
        try:
            eval_file_path = self.model_evaluation_config.model_evaluation_file_path
            model_eval_content = read_yaml_file(file_path=eval_file_path)
            model_eval_content = dict() if model_eval_content is None else model_eval_content

            previous_best_model = None
            if BEST_MODEL_KEY in model_eval_content:
                previous_best_model = model_eval_content[BEST_MODEL_KEY]

            logging.info(f"Previous eval result: {model_eval_content}")
            eval_result = {
                BEST_MODEL_KEY: {
                    MODEL_PATH_KEY: model_evaluation_artifact.evaluated_model_path,
                }
            }

            if previous_best_model is not None:
                model_history = {self.model_evaluation_config.time_stamp: previous_best_model}
                if HISTORY_KEY not in model_eval_content:
                    history = {HISTORY_KEY: model_history}
                    eval_result.update(history)
                else:
                    model_eval_content[HISTORY_KEY].update(model_history)

            model_eval_content.update(eval_result)
            logging.info(f"Updated eval result:{model_eval_content}")
            write_yaml_file(file_path=eval_file_path, data=model_eval_content)

        except Exception as e:
            raise ConcreteException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            trained_model_file_path = self.model_trainer_artifact.trained_model_file_path
            trained_model_object = load_object(file_path=trained_model_file_path)

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            schema_file_path = self.data_validation_artifact.schema_file_path

            train_dataframe = load_data(file_path=train_file_path,
                                        schema_file_path=schema_file_path,
                                        )
            test_dataframe = load_data(file_path=test_file_path,
                                       schema_file_path=schema_file_path,
                                       )
            schema_content = read_yaml_file(file_path=schema_file_path)
            target_column_name = schema_content[TARGET_COLUMNS_KEY]

            # target_column
            logging.info(f"Converting target column into numpy array.")
            train_target_arr = np.array(train_dataframe[target_column_name])
            test_target_arr = np.array(test_dataframe[target_column_name])
            logging.info(f"Conversion completed target column into numpy array.")

            # dropping target column from the dataframe
            logging.info(f"Dropping target column from the dataframe.")
            train_dataframe.drop(target_column_name, axis=1, inplace=True)
            test_dataframe.drop(target_column_name, axis=1, inplace=True)
            logging.info(f"Dropping target column from the dataframe completed.")

            model = self.get_best_model()

            if model is None:
                logging.info("Not found any existing model. Hence accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")
                return model_evaluation_artifact

            model_list = [model, trained_model_object]

            metric_info_artifact = evaluate_regression_model(model_list=model_list,
                                                             X_train=train_dataframe,
                                                             y_train=train_target_arr,
                                                             X_test=test_dataframe,
                                                             y_test=test_target_arr,
                                                             base_accuracy=self.model_trainer_artifact.model_accuracy,
                                                             )
            logging.info(f"Model evaluation completed. model metric artifact: {metric_info_artifact}")

            if metric_info_artifact is None:
                response = ModelEvaluationArtifact(is_model_accepted=False,
                                                   evaluated_model_path=trained_model_file_path
                                                   )
                logging.info(response)
                return response

            if metric_info_artifact.index_number == 1:
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=True)
                self.update_evaluation_report(model_evaluation_artifact)
                logging.info(f"Model accepted. Model eval artifact {model_evaluation_artifact} created")

            else:
                logging.info("Trained model is no better than existing model hence not accepting trained model")
                model_evaluation_artifact = ModelEvaluationArtifact(evaluated_model_path=trained_model_file_path,
                                                                    is_model_accepted=False)
            return model_evaluation_artifact
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def __del__(self):
        logging.info(f"{'=' * 20}Model Evaluation log completed.{'=' * 20} ")
