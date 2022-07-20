<div id="top"></div>

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">Concrete Compressive Strength Prediction</h3>

  <p align="center">
    Machine Learning Project
    <br />
    <a href="https://github.com/Mayankgaj/concrete_compressive_strength_prediction"><strong>Explore the Repo »</strong></a>
    <br />
    <br />
  </p>
</div>

### Software and account Requirement.

1. [GitHub Account](https://github.com)
2. [Heroku Account](https://dashboard.heroku.com/login)
3. [Kaggle Account](https://www.kaggle.com/)
4. [Py Charm IDE](https://www.jetbrains.com/pycharm/download/)
5. [GIT Cli](https://git-scm.com/downloads)
6. [GIT Documentation](https://git-scm.com/docs/gittutorial)


Creating conda environment
```
conda create -p venv python==3.9 -y
```
```
conda activate venv/
```
OR 
```
conda activate venv
```

```
pip install -r requirements.txt
```

Add Environment Variables
```
KAGGLE_USERNAME = < username of kaggle >
KAGGLE_KEY = < API key of kaggle >
```
Username and Key can be found in json file after Generating API key.

### About Project
 This project will be based on a dataset obtained from the Kaggle website. 
 The dataset consists of 1030 observations under 9
 attributes. The attributes consist of 8 quantitative inputs and 1
 quantitative output. The dataset does not contain any missing values.
 The dataset is focused on the compressive strength of a 
 concrete. The attributes include factors that affect concrete
 strength such as cement, water, aggregate (coarse and fine), 
 and fly ash etc… The objective of this project is trying to
 predict the concrete compressive strength based important 
 predictors. The study will consist of evaluating the impact 
 of different factors such as cement, water, age, fly ash, and
 or additives. We will evaluate the components that are highly
 correlated with concrete compressive strength and other 
 components that are less influential and can be neglected 
 through visualization or correlation matrix. In this study, 
 we will use different machine learning techniques to predict 
 the concrete compressive strength. Different modeling 
 techniques will be used for the prediction. The modeling 
 technique will include multiple linear regression, decision tree,
 and random forest, etc. A comparative analysis will be performed 
 to identify the best model for our prediction in terms of
 accuracy. The best model will be helpful for civil engineers
 in choosing the appropriate concrete for bridges, houses 
 construction.


## Steps to approach model
1. Data Ingestion
2. Data Validation
3. Data Transformation
4. Model Trainer
5. Model Evaluation
6. Model Pusher

### 1. Data Ingestion

In data ingestion we download the dataset from kaggle website
in raw formant with the help of [kaggle API](https://www.kaggle.com/docs/api), then we separate raw file into two files (train and test)
with the help of [train_test_split()](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)

### 2. Data Validation

In data validation we check number of columns, name of columns and target column with the schema file in test and train file,
also it checks does test and train file exist or not . After that it checks Data Drift in the train file with the help of test
file and save it in html and json format.

### 3. Data Transformation

In data transformation we do preprocessing with the [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)
on both train and test file and save it in array format.

### 4. Model Trainer

In model trainer we train the model on based on model config and check the accuracy based on user mention in config file.
we have used [LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html) , [RidgeRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html?highlight=ridge#sklearn.linear_model.Ridge) 
, [LassoRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html?highlight=lasso#sklearn.linear_model.Lasso) , [DecisionTreeRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeRegressor.html?highlight=decisiontreeregressor#sklearn.tree.DecisionTreeRegressor)
, [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html?highlight=randomforestregressor#sklearn.ensemble.RandomForestRegressor) and [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html?highlight=gridsearchcv#sklearn.model_selection.GridSearchCV) for hyper tuning.

### 5. Model Evaluation

In model evaluation we have check best model which have trained and 
test accuracy difference is 0.01 and not more than that. 
If it has more than that we will reject that model and will 
use other model.

### 6. Model Pusher

In Model pusher we push best model from model evaluation and
use it to predict concrete compressive strength.

## Structure of Project

```
oncrete_compressive_strength_prediction
   ├── config
   |   ├──config.yaml --> Essential Values For configuration 
   |   ├──model.yaml --> Essential Values for model training
   │   └──schema.yaml --> Essential Values for Data Evaluation of dataset
   ├── concret
   |   ├──component
   |   |  ├──data_ingestion.py 
   |   |  ├──data_transformation.py
   |   |  ├──data_validation.py
   |   |  ├──model_evaluation.py
   |   |  ├──model_pusher.py
   |   |  └──model_trainer.py
   |   ├──config
   |   |  └──configuration.py --> Classs and Functions created for components to get artifact paths and config path
   |   ├──constant
   |   |  └──_init_.py --> Declared the folder and files names from config (root folder) to config (concrete/config)
   |   ├──entity
   |   |  ├──_init_.py
   |   |  ├──artifact_entity.py --> For defining Named tuple skeleton for artifact related operation
   |   |  ├──config_entity.py --> For defining Named tuple skeleton for configuration related operation
   |   |  └──model_factory.py --> For training model and creating YAML template for training model
   |   ├──exception
   |   |  └──_init_.py --> Custom Exception to get line and file name to see errors  
   |   ├──logger
   |   |  └──_init_.py --> To get logs based on timestamp
   |   ├──pipeline
   |   |  └──pipeline.py --> To run the setup
   │   └──util
   |      ├──_init_.py
   |      └──util.py
   ├── .github
   |   └──workflows
   |      └──main.yaml --> YAML file for Heroku/Amazon deployment using GitHub Action and Creating docker container
   |── app.py 
   |── requirement.txt
   |── setup.py
   └── Dockerfile --> File for creating docker image
```



# Web Deployment

Link:- [Concrete_compressive_strength_prediction](https://concrete-predictor.herokuapp.com/)

![](/images/Screenshot.png)


## Tools Used

![](https://freepngimg.com/thumb/python_logo/5-2-python-logo-png-image-thumb.png)   <img height="200" src="https://dashboard.snapcraft.io/site_media/appmedia/2017/11/PyCharmCore256.png" width="200"/>   <img height="200" src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Visual_Studio_Code_1.35_icon.svg/2048px-Visual_Studio_Code_1.35_icon.svg.png" width="200"/> 
