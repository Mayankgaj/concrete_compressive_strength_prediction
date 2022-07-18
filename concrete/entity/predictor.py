import os
import sys

from concrete.exception import ConcreteException
from concrete.util.util import load_object

import pandas as pd


class ConcreteData:

    def __init__(self,
                 cement: float,
                 blast_furnace_slag: float,
                 fly_ash: float,
                 water: float,
                 superplasticizer: float,
                 coarse_aggregate: float,
                 fine_aggregate: float,
                 age: int
                 ):
        try:
            self.cement = cement
            self.blast_furnace_slag = blast_furnace_slag
            self.fly_ash = fly_ash
            self.water = water
            self.superplasticizer = superplasticizer
            self.coarse_aggregate = coarse_aggregate
            self.fine_aggregate = fine_aggregate
            self.age = age
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def get_concrete_input_data_frame(self):
        try:
            input_data = {
                'cement': [self.cement],
                'blast_furnace_slag': [self.blast_furnace_slag],
                'fly_ash': [self.fly_ash],
                'water': [self.water],
                'superplasticizer': [self.superplasticizer],
                'coarse_aggregate': [self.coarse_aggregate],
                'fine_aggregate': [self.fine_aggregate],
                'age': [self.age]}
            return pd.DataFrame(input_data)
        except Exception as e:
            raise ConcreteException(e, sys) from e


class ConcretePredictor:

    def __init__(self, model_dir: str):
        try:
            self.model_dir = model_dir
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def get_latest_model_path(self):
        try:
            folder_name = list(map(int, os.listdir(self.model_dir)))
            latest_model_dir = os.path.join(self.model_dir, f"{max(folder_name)}")
            file_name = os.listdir(latest_model_dir)[0]
            latest_model_path = os.path.join(latest_model_dir, file_name)
            return latest_model_path
        except Exception as e:
            raise ConcreteException(e, sys) from e

    def predict(self, X):
        try:
            model_path = self.get_latest_model_path()
            model = load_object(file_path=model_path)
            median_house_value = model.predict(X)
            return median_house_value
        except Exception as e:
            raise ConcreteException(e, sys) from e
