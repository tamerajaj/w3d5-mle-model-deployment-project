# Model deployment project

## Project description

In this project you will `train` and `deploy` a `machine learning model` on the `yellow taxi` dataset. The goal is to predict the `duration` of a trip.
You should use the `scikit-learn` library to train a `random forest regressor` model.
And deploy the model with one of the methods you saw this week.

## Project structure

The project is composed of 3 parts:

- Train the model with a `random forest regressor` track it with MLFlow.
- Deploy the model.
- Make a request to the model.

Bonus tasks if you have the time:

Bonus: Use the testing methods you saw this week to test your data and your model.

Bonus: Use `gridsearch` ot `optuna` to find the best hyperparameters for your model.

## Dataset

Yellow taxi dataset: https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page

- Year 2021
- Month 01


## Answer these questions

1. What is the RMSE of your model?
2. Which deployment method did you use?
3. What would you do differently if you had more time?


## How to submit your project

Upload your project on GitHub and send us the link. Answer the questions above in the README.md file.

## Setup
### Pipenv
```bash
pyenv local 3.10.9
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### Poetry
```shell
poetry config virtualenvs.in-project true
poetry install
```


```shell
source .venv/bin/activate
poetry add $( cat requirements.txt ) 	
```