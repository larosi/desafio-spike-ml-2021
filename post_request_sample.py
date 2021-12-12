# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 22:36:12 2021

@author: Mico
"""

import pandas as pd
import json
import requests
import random
from datetime import datetime

def do_post(body_dict, ip='127.0.0.1', port=8889, route='predict_by_date'):
    body_json = json.dumps(body_dict)
    localhost_url = f'http://{ip}:{port}/{route}'
    r = requests.post(localhost_url, data = body_json)
    return r

data_path = r'data/processed/merged.csv'

df = pd.read_csv(data_path)
df = df.drop(['Precio_leche'], axis = 1)

random_idx = random.randint(3, df.shape[0]-1)
random_slice = df.loc[random_idx-2:random_idx].reset_index(drop=True)

random_date = datetime(year=random_slice.ano.values[-1], month=random_slice.mes.values[-1], day=1)
random_date_str = random_date.strftime("%d-%m-%Y")

""" Post request with date as Query """

body_dict = {'date' : random_date_str}
r = do_post(body_dict, ip='127.0.0.1', port=8889, route='predict_by_date')
print(r)
print(r.text)

""" Post request with tree consecutive rows as Query """

random_slice.drop(['ano','mes'], axis = 1, inplace=True)
body_dict = random_slice.to_dict()

r = do_post(body_dict, ip='127.0.0.1', port=8889, route='predict_by_rows')
print(r)
print(r.text)

