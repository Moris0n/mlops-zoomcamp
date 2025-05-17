import os
import pickle
import click
import mlflow

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# move to system param file
MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"

def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)

@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
@click.option(
    "--experiment_name",
    default="nyc-taxi-experiment",
    help="Name of the MLflow experiment to use"
)
def run_train(data_path: str, experiment_name: str):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(experiment_name)
    mlflow.autolog()

    # Load data
    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val,   y_val   = load_pickle(os.path.join(data_path, "val.pkl"))

    # Run and log automatically (no need to pass experiment_id)
    with mlflow.start_run(run_name="rf-train"):
        model = RandomForestRegressor(max_depth=10, random_state=0)
        model.fit(X_train, y_train)
        preds = model.predict(X_val)

        rmse = mean_squared_error(y_val, preds)
        print(f"Validation RMSE: {rmse:.4f}")

if __name__ == '__main__':
    run_train()
