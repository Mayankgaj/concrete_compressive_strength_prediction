from concrete.entity.artifact_entity import DataIngestionArtifact
from concrete.entity.config_entity import DataIngestionConfig
from sklearn.model_selection import train_test_split
from kaggle.api.kaggle_api_extended import KaggleApi
from concrete.exception import ConcreteException
from concrete.logger import logging
import pandas as pd
import sys, os


class DataIngestion:

    def __init__(self, data_ingestion_config: DataIngestionConfig):
        """
        Description: Function is used to get ingestion config
        param data_ingestion_config:
                author_username : username of the author
                kaggel_dataset_name : name of the dataset
                raw_data_dir: name of directory for download the dataset
                ingested_dir: name of directory where to split file
                ingested_train_dir: name of directory to save train file
                ingested_test_dir: name of directory to save test file
        """
        try:
            logging.info(f"{'>>' * 20}Data Ingestion log started.{'<<' * 20} ")
            self.data_ingestion_config = data_ingestion_config

        except Exception as e:
            raise ConcreteException(e, sys)

    def download_concrete_data(self, ) -> str:
        """
        Description: Function is used to download the data from kaggle website.
        return: Path of downloaded file from kaggle
        """
        try:
            # extraction remote url to download dataset
            username = self.data_ingestion_config.author_username
            dataset_name = self.data_ingestion_config.kaggel_dataset_name

            api = KaggleApi()
            api.authenticate()

            download_path = self.data_ingestion_config.raw_data_dir

            logging.info(f"Downloading file from :[https://www.kaggle.com/datasets/{username}/{dataset_name}] "
                         f"into :[{download_path}]")
            api.dataset_download_files(f'{username}/{dataset_name}', path=download_path, unzip=True)

            logging.info(f"File :[{download_path}] has been downloaded successfully.")
            return download_path

        except Exception as e:
            raise ConcreteException(e, sys) from e

    def split_data_as_train_test(self) -> DataIngestionArtifact:
        """
        Description: function is used to split the dataset into test and train file
        return:
            train_file_path: directory of train file
            test_file_path: directory of test file
            is_ingested: True if ingested or False
            message: message after completing
        """
        try:
            raw_data_dir = self.data_ingestion_config.raw_data_dir

            file_name = os.listdir(raw_data_dir)[0]

            concrete_file_path = os.path.join(raw_data_dir, file_name)

            logging.info(f"Reading csv file: [{concrete_file_path}]")
            concrete_data_frame = pd.read_csv(concrete_file_path)

            logging.info(f"Splitting data into train and test")

            strat_train_set, strat_test_set = train_test_split(concrete_data_frame, test_size=0.2, random_state=42)

            train_file_path = os.path.join(self.data_ingestion_config.ingested_train_dir,
                                           file_name)

            test_file_path = os.path.join(self.data_ingestion_config.ingested_test_dir,
                                          file_name)

            if strat_train_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_train_dir, exist_ok=True)
                logging.info(f"Exporting training dataset to file: [{train_file_path}]")
                strat_train_set.to_csv(train_file_path, index=False)

            if strat_test_set is not None:
                os.makedirs(self.data_ingestion_config.ingested_test_dir, exist_ok=True)
                logging.info(f"Exporting testing dataset to file: [{test_file_path}]")
                strat_test_set.to_csv(test_file_path, index=False)

            data_ingestion_artifact = DataIngestionArtifact(train_file_path=train_file_path,
                                                            test_file_path=test_file_path,
                                                            is_ingested=True,
                                                            message=f"Data ingestion completed successfully."
                                                            )
            logging.info(f"Data Ingestion artifact:[{data_ingestion_artifact}]")
            return data_ingestion_artifact

        except Exception as e:
            raise ConcreteException(e, sys) from e

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """
        Description: Function is used to start data ingestion
        return: train and test file path with message
        """
        try:
            self.download_concrete_data()
            return self.split_data_as_train_test()
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def __del__(self):
        logging.info(f"{'>>' * 20}Data Ingestion log completed.{'<<' * 20} \n\n")
