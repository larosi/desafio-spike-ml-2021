# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 17:19:31 2021

@author: Mico
"""

import flask as flk
import json
import src.model.predictor as model_predictor
from src.data.dataset_cleasing import compute_std_mean_shift
import pandas as pd

app = flk.Flask(__name__)

MODEL_PATH = 'models/model.pkl'
MERGED_DF_PATH = 'data/processed/merged.csv'

df = pd.read_csv(MERGED_DF_PATH)
df = model_predictor.drop_leche(df)
my_model = model_predictor.load_sklearn_model(MODEL_PATH)

def parse_date(body):
    date_str = body['date']
    dia, mes, ano = date_str.split('-')
    return int(mes), int(ano)

@app.route('/')
def hello():
    return "Hola Spike"

@app.route('/predict_by_date', methods=['POST'])
def predict_by_date():
    body = flk.request.get_json(force=True)
    
    # parse date
    mes, ano = parse_date(body)
    
    mask = (df.mes==mes) & (df.ano==ano)
    idx = mask.values.argmax()
    
    if (idx-2 >=0) and (idx <=df.shape[0]-1):
        df_slice = df.loc[idx-2:idx].reset_index(drop=True)
        X = compute_std_mean_shift(df_slice)
        prediction = my_model.predict(X)
    else:
        prediction = [None]

    data = {'precio_leche': '{}'.format(str(prediction[0]))}
    
    return json.dumps(data)

@app.route('/predict_by_rows', methods=['POST'])
def predict_by_rows():
    body = flk.request.get_json(force=True)
    X = pd.DataFrame(data=body)
    X = compute_std_mean_shift(X)
    prediction = my_model.predict(X)

    data = {'precio_leche': '{}'.format(str(prediction[0]))}
    
    return json.dumps(data)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port=8889)