# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 16:58:48 2021

@author: Mico
"""

import pickle
import os
import pandas as pd
import numpy as np


def load_sklearn_model(model_path):
    with open(model_path, 'rb') as f:
        my_model = pickle.load(f)
    return my_model

def load_support_info(model_path):
    model_extension = os.path.splitext(model_path)[-1]
    output_support_path = model_path.split(model_extension)[0] + '.csv'
    
    df_support = pd.read_csv(output_support_path, index_col=False)
    support_columns = list(df_support.columns[df_support.loc[0].values])
    return df_support, support_columns

def get_required_columns_names(support_columns):
    generated_sufix = ['_shift3_std', '_shift3_mean', '_mes_anterior']
    required_raw_column_names = []
    for col in support_columns:
        for sufix in generated_sufix:
            col = col.replace(sufix, '')
        required_raw_column_names.append(col)
    required_raw_column_names = list(np.unique(required_raw_column_names))
    return required_raw_column_names

def drop_leche(X):
    cols_no_leche = [x for x in list(X.columns) if not ('leche' in x)]
    X = X[cols_no_leche]
    return X

""" model prediction example """
if __name__ == "__main__":
    import random
    from pathlib import Path
    import sys

    src_path = os.path.join(str(Path(__file__).parent.absolute()), '..')
    sys.path.append(src_path)
    from data.dataset_cleasing import compute_std_mean_shift
    
    merged_data_path = r'../../data/processed/merged.csv'
    model_path = r'../../models/model.pkl'
    
    df_dataset = pd.read_csv(merged_data_path, index_col=False)

    df_support, support_columns = load_support_info(model_path)
    my_model = load_sklearn_model(model_path)
    
    for _ in range(0, 10):
        random_idx = random.randint(3, df_dataset.shape[0]-1)
        random_slice = df_dataset.loc[random_idx-2:random_idx]
        
        random_slice_feature = compute_std_mean_shift(drop_leche(random_slice))
    
        prediction = my_model.predict(random_slice_feature)
        print('predicted milk price: ${}'.format(prediction[0]))