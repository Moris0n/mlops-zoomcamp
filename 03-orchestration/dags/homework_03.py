from datetime import datetime
from airflow.sdk import DAG, task   # 3.0’s stable authoring interface
import pandas as pd

with DAG(
    dag_id="orchestration",
    start_date=datetime(2025, 5, 30),
    schedule=None,          # manual run
    catchup=False,
    tags=["homework"],
) as dag:

    @task
    def question_2():
        print("Qeustion 2 : ")
        df = pd.read_parquet('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet')
        print(f"records: {df.shape} ")

    @task
    def read_dataframe(filename):
        df = pd.read_parquet(filename)

        df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
        df.duration = df.duration.dt.total_seconds() / 60

        df = df[(df.duration >= 1) & (df.duration <= 60)]

        categorical = ['PULocationID', 'DOLocationID']
        df[categorical] = df[categorical].astype(str)

        print(f"records: {df.shape} ")
        
        return df
        

    read_dataframe('https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet')