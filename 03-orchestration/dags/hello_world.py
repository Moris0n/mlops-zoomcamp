from datetime import datetime
from airflow.sdk import DAG, task   # 3.0’s stable authoring interface

with DAG(
    dag_id="hello_world",
    start_date=datetime(2025, 5, 30),
    schedule=None,          # manual run
    catchup=False,
    tags=["example"],
) as dag:

    @task
    def greet():
        print("👋  Hello from Airflow 3!")

    greet()
