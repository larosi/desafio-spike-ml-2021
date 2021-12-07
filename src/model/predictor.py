# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 16:58:48 2021

@author: Mico
"""

import pickle

def load_sklearn_model(model_path):
    with open(model_path, 'rb') as f:
        my_model = pickle.load(f)
    return my_model