import json
import pathlib
import pickle
from typing import List
from typing import Tuple

import pandas
from sklearn import model_selection
from sklearn import neighbors
from sklearn import pipeline
from sklearn import preprocessing
from sklearn import metrics
import numpy as np

SALES_PATH = "data/kc_house_data.csv"  # path to CSV with home sale data
DEMOGRAPHICS_PATH = "data/zipcode_demographics.csv"  # path to CSV with demographics
# List of columns (subset) that will be taken from home sale data
SALES_COLUMN_SELECTION = [
    'price', 'bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 'floors',
    'sqft_above', 'sqft_basement', 'zipcode'
]
OUTPUT_DIR = "model"  # Directory where output artifacts will be saved


def load_data(
    sales_path: str, demographics_path: str, sales_column_selection: List[str]
) -> Tuple[pandas.DataFrame, pandas.Series]:
    """Load the target and feature data by merging sales and demographics.

    Args:
        sales_path: path to CSV file with home sale data
        demographics_path: path to CSV file with home sale data
        sales_column_selection: list of columns from sales data to be used as
            features

    Returns:
        Tuple containg with two elements: a DataFrame and a Series of the same
        length.  The DataFrame contains features for machine learning, the
        series contains the target variable (home sale price).

    """
    data = pandas.read_csv(sales_path,
                           usecols=sales_column_selection,
                           dtype={'zipcode': str})
    demographics = pandas.read_csv(demographics_path,
                                   dtype={'zipcode': str})

    merged_data = data.merge(demographics, how="left",
                             on="zipcode").drop(columns="zipcode")
    # Remove the target variable from the dataframe, features will remain
    y = merged_data.pop('price')
    x = merged_data

    return x, y


def evaluate_model(model, x_train, y_train, x_test, y_test) -> dict:
    """Evaluate the model performance and return metrics.
    
    Args:
        model: Trained sklearn model
        x_train: Training features
        y_train: Training targets
        x_test: Test features
        y_test: Test targets
        
    Returns:
        Dictionary containing evaluation metrics
    """
    # Calculate scores
    train_score = model.score(x_train, y_train)
    test_score = model.score(x_test, y_test)
    
    # Make predictions on test set
    y_pred = model.predict(x_test)
    
    # Calculate additional metrics
    mae = metrics.mean_absolute_error(y_test, y_pred)
    mse = metrics.mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    # Determine fit status
    if train_score - test_score > 0.1:
        fit_status = "Overfitted"
        print("\nWARN: Potential overfitting!")
        print(f"Training score is {train_score - test_score:.4f} higher than test score")
    elif test_score < 0.6:
        fit_status = "Underfitted"
        print("\nWARN: Potential underfitting!")
        print(f"Test score is {test_score:.4f} (low performance on both training and test data)")
    else:
        fit_status = "Good Fit"
    
    # Create evaluation results dictionary
    evaluation_results = {
        "train_r2_score": train_score,
        "test_r2_score": test_score,
        "mean_absolute_error": mae,
        "root_mean_squared_error": rmse,
        "mean_actual_price": float(y_test.mean()),
        "mean_predicted_price": float(y_pred.mean()),
        "fit_status": fit_status
    }
    
    # Print evaluation results
    print("\nModel Performance Evaluation:")
    print("=" * 40)
    for key, value in evaluation_results.items():
        display_name = key.replace('_', ' ').title()
        if 'error' in key or 'price' in key:
            print(f"{display_name:<30} ${value:,.2f}")
        elif key == 'fit_status':
            print(f"{display_name:<30} {value}")
        else:
            print(f"{display_name:<30} {value:.4f}")
    print("=" * 40)

    # Return metrics dictionary
    return evaluation_results


def main():
    """Load data, train model, and export artifacts."""
    x, y = load_data(SALES_PATH, DEMOGRAPHICS_PATH, SALES_COLUMN_SELECTION)
    x_train, x_test, y_train, y_test = model_selection.train_test_split(
        x, y, random_state=42)

    model = pipeline.make_pipeline(preprocessing.RobustScaler(),
                                   neighbors.KNeighborsRegressor()).fit(
                                       x_train, y_train)

    # Evaluate the model performance
    evaluation_results = evaluate_model(model, x_train, y_train, x_test, y_test)

    output_dir = pathlib.Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)

    # Output model artifacts: pickled model and JSON list of features
    pickle.dump(model, open(output_dir / "model.pkl", 'wb'))
    json.dump(list(x_train.columns),
              open(output_dir / "model_features.json", 'w'))
    
    # Save evaluation metrics
    json.dump(evaluation_results, 
              open(output_dir / "model_evaluation.json", 'w'), 
              indent=2)


if __name__ == "__main__":
    main()
