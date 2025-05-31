from datetime import datetime
import pandas as pd
import pyarrow.parquet as pq
import requests

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(
    dag_id="orchestration",
    start_date=datetime(2025, 5, 30),
    schedule=None,
    catchup=False,
    tags=["homework"],
)
def training_pipeline():

    @task()
    def download_file():
        url = Variable.get("taxi_data_url")
        local_path = '/tmp/yellow_tripdata.parquet'
        response = requests.get(url)
        with open(local_path, 'wb') as f:
            f.write(response.content)
        return local_path

    @task()
    def read_and_process(path):
        df = pd.read_parquet(path)
        df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
        df.duration = df.duration.dt.total_seconds() / 60
        df = df[(df.duration >= 1) & (df.duration <= 60)]
        categorical = ['PULocationID', 'DOLocationID']
        df[categorical] = df[categorical].astype(str)

        processed_path = '/tmp/processed.parquet'
        df.to_parquet(processed_path, index=False)
        return processed_path

    @task()
    def train_model(processed_data_path):
        df = pd.read_parquet(processed_data_path)
        # training logic here
        print(f"Training on {df.shape[0]} records")

    file_path = download_file()
    processed_path = read_and_process(file_path)
    train_model(processed_path)

dag = training_pipeline()
