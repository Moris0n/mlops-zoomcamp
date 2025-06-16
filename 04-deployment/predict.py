#!/usr/bin/env python
# coding: utf-8

import os
import sys

import uuid
import pickle

from datetime import datetime

import pandas as pd

import mlflow

from prefect import task, flow, get_run_logger
from prefect.context import get_run_context

from dateutil.relativedelta import relativedelta

from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import make_pipeline


from datetime import datetime

def generate_ride_ids(df):
    today = datetime.today()
    year = today.year
    month = today.month
    ride_ids = f'{year:04d}/{month:02d}_' + df.index.astype(str)
    return ride_ids

with  open('model.bin', 'rb') as f_in :
    (dv, model) = pickle.load(f_in)

def read_dataframe(filename: str):
    df = pd.read_parquet(filename)

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    
    df['ride_id'] = generate_ride_ids(len(df))

    return df

def prepare_dictionaries(df: pd.DataFrame):
    categorical = ['PULocationID', 'DOLocationID']
    dicts = df[categorical].to_dict(orient='records')
    return dicts

def predict(feautres):
    X = dv.transform(feautres)
    pred = model.predict(X)
    return pred[0]

def save_results(df, y_pred, output_file):
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']

    df_result.to_parquet(output_file, index=False)

app = Flask('duration-prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoinnt():
    ride = request.get_json()

    features = prepare_feautres(ride)
    pred = predict(features)
    result = {
        "duration" : pred
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
