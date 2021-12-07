# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 22:36:12 2021

@author: Mico
"""

import pandas as pd
import json
import requests


data_path = r'data/processed/precio_leche.csv'

df = pd.read_csv(data_path)
df = df.drop(['Precio_leche'], axis = 1)
random_sample = df.sample(n=1)


body_dict = {}
for i in range(0, random_sample.shape[1]):
    key = random_sample.columns[i]
    val = random_sample.values[0][i]
    body_dict[key] = val

body_json = json.dumps(body_dict)

route = 'model_api'
port = 8889
localhost_url = f'http://127.0.0.1:{port}/{route}'
header = {'Contect-type': 'application/json'}
r = requests.post(localhost_url, data = body_json)

print(r)
print(r.text)
