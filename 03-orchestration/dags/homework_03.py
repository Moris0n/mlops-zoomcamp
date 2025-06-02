from datetime import datetime
from pathlib import Path
import pickle
import math
import mlflow
import pandas as pd

from airflow.decorators import dag, task
from airflow.models import Variable

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression       # ← we need intercept_
from sklearn.metrics import mean_squared_error

# ---------------------------------------------------------------------
# constants & helpers
# ---------------------------------------------------------------------
DATA_DIR = Path("/opt/airflow/data")
RAW_DIR = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)


def _download(url: str, dst: Path) -> str:
    """Download a parquet file and pickle it locally (returns path)."""
    df = pd.read_parquet(url)
    df.to_pickle(dst)
    return str(dst)


def setup_mlflow() -> None:
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("airflow-model")


def preprocess(
    df: pd.DataFrame,
    dv: DictVectorizer | None = None,
    fit_dv: bool = False
):
    categorical = ["PULocationID", "DOLocationID"]
    numerical = ["trip_distance"]

    df["duration"] = (
        df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    ).dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()  # ← Fix here

    df[categorical] = df[categorical].astype(str)

    y = df["duration"].values
    dicts = df[categorical + numerical].to_dict(orient="records")

    if fit_dv:
        dv = DictVectorizer()
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, y, dv


# ---------------------------------------------------------------------
# Airflow tasks
# ---------------------------------------------------------------------
@task()
def download_split(split: str) -> str:
    url = Variable.get(f"taxi_data_url_{split}")
    raw_path = RAW_DIR / f"{split}.pkl"
    return _download(url, raw_path)


@task()
def preprocess_and_save(raw_path: str, fit_dv: bool) -> str:
    """
    Load raw pickle → preprocess → save (X, y) pickle.
    If `fit_dv` is True, trains and saves the DictVectorizer.
    """
    df = pd.read_pickle(raw_path)

    dv_path = DATA_DIR / "dv.pkl"
    dv = None
    if not fit_dv:
        with open(dv_path, "rb") as f:
            dv = pickle.load(f)

    X, y, dv = preprocess(df, dv=dv, fit_dv=fit_dv)

    # persist DictVectorizer once (train split)
    if fit_dv:
        with open(dv_path, "wb") as f:
            pickle.dump(dv, f)

        setup_mlflow()
        with mlflow.start_run(run_name="vectorizer", nested=True):
            mlflow.log_artifact(str(dv_path), artifact_path="preprocessor")

    # save processed dataset (do NOT overwrite raw data)
    split = Path(raw_path).stem          # 'train' / 'val' / 'test'
    out_path = PROC_DIR / f"{split}.pkl"
    with open(out_path, "wb") as f:
        pickle.dump((X, y), f)

    return str(out_path)


@task()
def train_model(train_path: str, val_path: str):
    with open(train_path, "rb") as f:
        X_train, y_train = pickle.load(f)
    with open(val_path, "rb") as f:
        X_val, y_val = pickle.load(f)

    setup_mlflow()

    with mlflow.start_run(run_name="linreg-model"):
        model = LinearRegression()
        model.fit(X_train, y_train)

        # --- print & log intercept ---
        print(f"Model intercept_: {model.intercept_:.4f}")
        mlflow.log_param("intercept", model.intercept_)

        val_rmse = math.sqrt(mean_squared_error(y_val, model.predict(X_val)))
        mlflow.log_metric("val_rmse", val_rmse)
        mlflow.sklearn.log_model(model, artifact_path="model")
        print(f"Validation RMSE: {val_rmse:.3f}")


# ---------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------
@dag(
    dag_id="ml_pipeline_vectorized",
    start_date=datetime(2025, 5, 31),
    schedule=None,
    catchup=False,
    tags=["homework", "dictvec"],
)
def pipeline():

    # 1. download splits
    train_raw = download_split("train")
    # val_raw   = download_split("val")
    # test_raw  = download_split("test")

    # 2. preprocess (train fits dv, others transform)
    train_pp = preprocess_and_save(train_raw, fit_dv=True)
    # val_pp = preprocess_and_save(val_raw, fit_dv=False)
    # test_pp = preprocess_and_save(test_raw, fit_dv=False)

   # train_pp >> [val_pp, test_pp]

    # 3. train model
    train_model(train_pp, train_pp)


dag = pipeline()
