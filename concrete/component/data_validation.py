from concrete.entity.artifact_entity import DataValidationArtifact, DataIngestionArtifact
from concrete.entity.config_entity import DataValidationConfig
from concrete.exception import ConcreteException
from concrete.util.util import read_yaml_file
from concrete.logger import logging
from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection
from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab
import json
import pandas as pd
import os, sys


class DataValidation:

    def __init__(self, data_validation_config: DataValidationConfig,
                 data_ingestion_artifact: DataIngestionArtifact):
        """
        Description: Function is used to get
                     Validation config to validate the column name,
                     number of columns and target columns
                     ingestion config to get the directory path
        param data_validation_config: schema_dir: directory name of schema file
                                      schema_file_name: name of schema file
                                      report_file_name: name of report of data drift
                                      report_page_file_name: name of the html file of report
        param data_ingestion_artifact: author_username : username of the author
                                       kaggel_dataset_name : name of the dataset
                                       raw_data_dir: name of directory for download the dataset
                                       ingested_dir: name of directory where to split file
                                       ingested_train_dir: name of directory to save train file
                                       ingested_test_dir: name of directory to save test file

        """
        try:
            logging.info(f"{'>>' * 20}Data Validation log started.{'<<' * 20} ")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def get_train_and_test_df(self):
        """
        Description: Function is used to read the train file and test file and convert it into dataframe
        return: train and test dataframe
        """
        try:
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            return train_df, test_df
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def is_train_test_file_exists(self) -> bool:
        try:
            logging.info("Checking if training and test file is available")

            is_train_file_exist = os.path.exists(self.data_ingestion_artifact.train_file_path)
            is_test_file_exist = os.path.exists(self.data_ingestion_artifact.test_file_path)

            is_available = is_train_file_exist and is_test_file_exist

            logging.info(f"Is train and test file exists?-> {is_available}")

            if not is_available:
                training_file = self.data_ingestion_artifact.train_file_path
                testing_file = self.data_ingestion_artifact.test_file_path
                message = f"Training file: {training_file} or Testing file: {testing_file}" \
                          "is not present"
                raise Exception(message)

            return is_available
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def validate_dataset_schema(self) -> bool:
        """
        Description: This Function is used to validate the train and test file with schema config
        return: Validating status True or False, True that schema config matches with train and test file
                False for not matching with schema config
        """
        try:
            config = read_yaml_file(self.data_validation_config.schema_file_path)
            len_col = config["number_of_column"]
            names_of_columns = list(config["columns"].keys())
            target_column = config["target_column"]
            train_df, test_df = self.get_train_and_test_df()

            # Checking train file
            train_checked: bool = True

            logging.info("Validating Train file  with Schema file,"
                         f"Train file path {self.data_ingestion_artifact.train_file_path}"
                         f"Schema file path {self.data_validation_config.schema_file_path}")

            # Check number of columns in train file
            len_col_train = len(train_df.columns)
            if len_col != len_col_train:
                train_checked: bool = False
                logging.info("length of columns of Train file is not equal to length of columns in schema config"
                             f"length of columns in train file is {len_col_train}, required length is {len_col}")

            # Check column names in train file
            col_names = list(train_df.columns.str.rstrip()[:-1])
            if names_of_columns != col_names:
                train_checked: bool = False
                logging.info("columns name not matching with schema config in train file")

            # Check target column in train file
            target_column_name = train_df.columns[-1]
            if target_column != target_column_name:
                train_checked: bool = False
                logging.info("train file target column does not match with schema file")

            # test file
            test_checked: bool = True

            logging.info("Validating Test file  with Schema file"
                         f"Test file path {self.data_ingestion_artifact.test_file_path}"
                         f"Schema file path {self.data_validation_config.schema_file_path}")

            # Check number of columns in test file
            len_col_test = len(test_df.columns)
            if len_col != len_col_test:
                test_checked: bool = False
                logging.info("length of columns of Test file is not equal to length of columns in schema config"
                             f"length of columns in test file is {len_col_test}, required length is {len_col}")

            # Check column names in test file
            col_names = list(test_df.columns.str.rstrip()[:-1])
            if names_of_columns != col_names:
                test_checked: bool = False
                logging.info("columns name not matching with schema config in test file")

            # Check target column in test file
            target_column_name = test_df.columns[-1]
            if target_column != target_column_name:
                test_checked: bool = False
                logging.info("test file target column does not match with schema file")

            validation_status = train_checked and test_checked

            return validation_status
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def get_and_save_data_drift_report(self):
        """
        Description: Function is used to get the report of data drift in the train and test file
        return: It returns the report of data drift in json file
        """
        try:
            profile = Profile(sections=[DataDriftProfileSection()])

            train_df, test_df = self.get_train_and_test_df()

            profile.calculate(train_df, test_df)

            report = json.loads(profile.json())

            report_file_path = self.data_validation_config.report_file_path
            report_dir = os.path.dirname(report_file_path)
            os.makedirs(report_dir, exist_ok=True)

            with open(report_file_path, "w") as report_file:
                json.dump(report, report_file, indent=6)
            return report
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def save_data_drift_report_page(self):
        """
        Description: Function is used to get the report of data drift in the train and test file
        return: It returns the report in html format to view it
        """
        try:
            dashboard = Dashboard(tabs=[DataDriftTab()])
            train_df, test_df = self.get_train_and_test_df()
            dashboard.calculate(train_df, test_df)

            report_page_file_path = self.data_validation_config.report_page_file_path
            report_page_dir = os.path.dirname(report_page_file_path)
            os.makedirs(report_page_dir, exist_ok=True)

            dashboard.save(report_page_file_path)
        except Exception as e:
            raise ConcreteException(e, sys)from e

    def is_data_drift_found(self) -> bool:
        """
        Description: Function is used to get if data drift found or not
        return: True if data drift found or False if not found
        """
        try:
            report = self.get_and_save_data_drift_report()
            self.save_data_drift_report_page()
            return True
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        Description: This function is used to start the data validation
        return: schema_dir: directory name of schema file
                            schema_file_name: name of schema file
                            report_file_name: name of report of data drift
                            report_page_file_name: name of the html file of report
        """
        try:
            self.is_train_test_file_exists()
            self.validate_dataset_schema()
            self.is_data_drift_found()

            data_validation_artifact = DataValidationArtifact(
                schema_file_path=self.data_validation_config.schema_file_path,
                report_file_path=self.data_validation_config.report_file_path,
                report_page_file_path=self.data_validation_config.report_page_file_path,
                is_validated=True,
                message="Data Validation performed successfully."
            )
            logging.info(f"Data validation artifact: {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def __del__(self):
        logging.info(f"{'>>' * 20}Data Validation log completed.{'<<' * 20} \n\n")
