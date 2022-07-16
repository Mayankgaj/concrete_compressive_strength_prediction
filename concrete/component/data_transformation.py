from concrete.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact, \
    DataTransformationArtifact
from concrete.util.util import load_data, read_yaml_file, save_numpy_array_data, save_object
from concrete.entity.config_entity import DataTransformationConfig
from sklearn.preprocessing import StandardScaler
from concrete.exception import ConcreteException
from concrete.logger import logging
from concrete.constant import *
import numpy as np
import sys, os


class DataTransformation:

    def __init__(self, data_transformation_config: DataTransformationConfig,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_artifact: DataValidationArtifact
                 ):
        """
        Description: This Function is used to get the data transformation ,data ingestion and
                     data validation config
        param data_transformation_config: transformed_dir: Directory name where data transformation will save
                                          transformed_train_dir: Directory name where train transformed file will save
                                          transformed_test_dir: Directory name where test transformed file will save
                                          preprocessing_dir: Directory name where preprocessed file will save
                                          preprocessed_object_file_name: File name of preprocessed
        param data_ingestion_artifact: author_username : username of the author
                                       kaggel_dataset_name : name of the dataset
                                       raw_data_dir: name of directory for download the dataset
                                       ingested_dir: name of directory where to split file
                                       ingested_train_dir: name of directory to save train file
                                       ingested_test_dir: name of directory to save test file
        param data_validation_artifact: schema_dir: directory name of schema file
                                      schema_file_name: name of schema file
                                      report_file_name: name of report of data drift
                                      report_page_file_name: name of the html file of report
        """
        try:
            logging.info(f"{'=' * 20}Data Transformation log started.{'=' * 20} ")
            self.data_transformation_config = data_transformation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_artifact = data_validation_artifact

        except Exception as e:
            raise ConcreteException(e, sys) from e

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        Description: Function is used to standardize the data(train and test both) with standard scaler and
                     saved it in array form
        return: is_transformed: Ture for transform and False for not transform
                message: message after data transform completed
                transformed_train_file_path: Path of transformed train file
                transformed_test_file_path: Path of transformed test file
                preprocessed_object_file_path: Save preprocessed object for predict data
        """
        try:
            logging.info(f"Obtaining preprocessing object.")
            preprocessing_obj = StandardScaler()

            logging.info(f"Obtaining training and test file path.")
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            schema_file_path = self.data_validation_artifact.schema_file_path

            logging.info(f"Loading training and test data as pandas dataframe.")
            train_df = load_data(file_path=train_file_path, schema_file_path=schema_file_path)

            test_df = load_data(file_path=test_file_path, schema_file_path=schema_file_path)

            schema = read_yaml_file(file_path=schema_file_path)

            target_column_name = schema[TARGET_COLUMNS_KEY]

            logging.info(f"Splitting input and target feature from training and testing dataframe.")
            input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
            target_feature_train_df = train_df[target_column_name]

            input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
            target_feature_test_df = test_df[target_column_name]

            logging.info(f"Applying preprocessing object on training dataframe and testing dataframe")
            input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)

            train_arr = np.c_[input_feature_train_arr, np.array(target_feature_train_df)]

            test_arr = np.c_[input_feature_test_arr, np.array(target_feature_test_df)]

            transformed_train_dir = self.data_transformation_config.transformed_train_dir
            transformed_test_dir = self.data_transformation_config.transformed_test_dir

            train_file_name = os.path.basename(train_file_path).replace(".csv", ".npz")
            test_file_name = os.path.basename(test_file_path).replace(".csv", ".npz")

            transformed_train_file_path = os.path.join(transformed_train_dir, train_file_name)
            transformed_test_file_path = os.path.join(transformed_test_dir, test_file_name)

            logging.info(f"Saving transformed training and testing array.")

            save_numpy_array_data(file_path=transformed_train_file_path, array=train_arr)
            save_numpy_array_data(file_path=transformed_test_file_path, array=test_arr)

            preprocessing_obj_file_path = self.data_transformation_config.preprocessed_object_file_path

            logging.info(f"Saving preprocessing object.")
            save_object(file_path=preprocessing_obj_file_path, obj=preprocessing_obj)

            data_transformation_artifact = DataTransformationArtifact(is_transformed=True,
                                                                      message="Data transformation successfully.",
                                                                      transformed_train_file_path=transformed_train_file_path,
                                                                      transformed_test_file_path=transformed_test_file_path,
                                                                      preprocessed_object_file_path=preprocessing_obj_file_path

                                                                      )
            logging.info(f"Data transformation artifact: {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def __del__(self):
        logging.info(f"{'=' * 20}Data Transformation log completed.{'=' * 20} \n\n")
