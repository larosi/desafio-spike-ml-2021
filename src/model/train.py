# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 15:12:23 2021

@author: Mico
"""

import argparse
import pandas as pd
import pickle

# notebook imports
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import SelectKBest, mutual_info_regression


def save_sklearn_model(model, model_path):
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
def load_data(dataframe_path):
    precio_leche_pp_pib = pd.read_csv(dataframe_path)
    X = precio_leche_pp_pib.drop(['Precio_leche'], axis = 1)
    y = precio_leche_pp_pib['Precio_leche']

    return X, y

def get_arguments():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-i',
                        '--input_data_path',
                        type=str,
                        default="data/processed/precio_leche.csv",
                        help='Path to yaml config file.')
    
    my_parser.add_argument('-o',
                        '--output_model_path',
                        type=str,
                        default="models/model.pkl",
                        help='Path to save the trained model')
    
    return my_parser.parse_args()

""" load data and arguments """
args = get_arguments()

dataframe_path = args.input_data_path
output_model_path = args.output_model_path

X,y = load_data(dataframe_path)

""" trainer logic defined on the notebook """

# generate random data-set
np.random.seed(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipe = Pipeline([('scale', StandardScaler()),
                 ('selector', SelectKBest(mutual_info_regression)),
                 ('poly', PolynomialFeatures()),
                 ('model', Ridge())])
k=[3, 4, 5, 6, 7, 10]
alpha=[1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
poly = [1, 2, 3, 5, 7]
grid = GridSearchCV(estimator = pipe,
                    param_grid = dict(selector__k=k,
                                      poly__degree=poly,
                                      model__alpha=alpha),
                    cv = 3,
                   scoring = 'r2')
grid.fit(X_train, y_train)
y_predicted = grid.predict(X_test)

# evaluar modelo
rmse = mean_squared_error(y_test, y_predicted)
r2 = r2_score(y_test, y_predicted)

# printing values
print('RMSE: ', rmse)
print('R2: ', r2)

""" export trained model into a pickle """
save_sklearn_model(model=grid, model_path=output_model_path)