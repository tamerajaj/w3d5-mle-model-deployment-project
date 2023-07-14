# import json
import os
import sys

# import click
import mlflow
import optuna

# import pandas as pd
from dotenv import load_dotenv
from optuna.integration.mlflow import MLflowCallback
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from helper_functions import get_data, preprocess

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
load_dotenv()
# TODO: make logging work for all runs of optuna


def train():
    """Train the model."""
    dataset = get_data()
    # df_processed = preprocess(dataset)

    y = dataset["trip_duration_minutes"].values
    X = dataset.drop(columns=["trip_duration_minutes"])
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=42, test_size=0.2
    )

    dv = DictVectorizer()
    X_train, dv = preprocess(X_train, dv, fit_dv=True)
    X_test, _ = preprocess(X_test, dv, fit_dv=False)
    features = ["PULocationID", "DOLocationID", "trip_distance"]
    target = "duration"

    load_dotenv()
    year = os.getenv("YEAR")
    month = int(os.getenv("MONTH"))
    color = os.getenv("COLOR")
    tags = {
        "model": "random forest regressor",
        "dataset": f"{color}-taxi",
        "year": year,
        "month": month,
        "features": features,
        "target": target,
    }

    mlflc = MLflowCallback(
        tracking_uri=os.getenv("MLFLOW_TRACKING_URI"),
        metric_name="RMSE",
        mlflow_kwargs={"tags": tags},
    )

    @mlflc.track_in_mlflow()
    def objective(trial):
        # Define the search space for hyperparameters
        criterion = trial.suggest_categorical("criterion", ["squared_error"])
        max_depth = trial.suggest_int("max_depth", 1, 20)
        min_samples_split = trial.suggest_int("min_samples_split", 2, 10)
        min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 4)
        n_estimators = trial.suggest_int("n_estimators", 10, 50)
        # Create a random forest regressor with the hyperparameters
        rf_regressor = RandomForestRegressor(
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            n_estimators=n_estimators,
            # n_jobs=-1,
        )

        # Train the regressor
        rf_regressor.fit(X_train, y_train)

        # Make predictions on the test set
        y_pred = rf_regressor.predict(X_test)

        # Calculate the root mean squared error (RMSE)
        rmse = mean_squared_error(y_test, y_pred, squared=False)

        return rmse

    # Perform hyperparameter optimization with Optuna
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=20, callbacks=[mlflc])

    # Get the best trial and parameters
    best_trial = study.best_trial
    best_params = best_trial.params

    # Log the Optuna search results to MLflow
    mlflow.log_params(best_params)
    mlflow.log_metric("best_rmse", best_trial.value)

    # Create a random forest regressor with the best hyperparameters
    rf_regressor = RandomForestRegressor(
        criterion=best_params["criterion"],
        max_depth=best_params["max_depth"],
        min_samples_split=best_params["min_samples_split"],
        min_samples_leaf=best_params["min_samples_leaf"],
        n_estimators=best_params["n_estimators"],
        # n_jobs=-1,
    )

    print("Training the model...")
    rf_regressor.fit(X_train, y_train)

    y_pred = rf_regressor.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)

    mlflow.log_metric("rmse", rmse)

    mlflow.sklearn.log_model(rf_regressor, "random-forest-fare-model")


if __name__ == "__main__":
    train()
