# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 17:19:31 2021

@author: Mico
"""

import flask as flk
import json
import src.model.predictor as model_predictor
import pandas as pd

app = flk.Flask(__name__)

MODEL_PATH = 'models/model.pkl'
my_model = model_predictor.load_sklearn_model(MODEL_PATH)

@app.route('/')
def hello():
    return "Hola Spike"

@app.route('/model_api', methods=['POST'])
def model_api():
    body = flk.request.get_json(force=True)
    X = pd.DataFrame(data=body, index=[0])
    prediction = my_model.predict(X)

    data = {'precio_leche': '{}'.format(str(prediction[0]))}
    
    return json.dumps(data)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port=8889)