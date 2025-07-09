"""
Simple Feature Evaluation for Sound Realty House Price Prediction

Quick analysis to find the best features to add to the model.
"""

import pandas as pd
import json
from pathlib import Path

def main():
    """Find the best features to add to the model."""
    print("SOUND REALTY - FEATURE EVALUATION")
    print("=" * 50)
    
    # Load data
    data = pd.read_csv("../data/kc_house_data.csv", dtype={'zipcode': str})
    
    # Current features in the model
    current_features = ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                       'floors', 'sqft_above', 'sqft_basement']
    
    # Get correlations with price (only numeric columns)
    numeric_data = data.select_dtypes(include=['number'])
    correlations = numeric_data.corr()['price'].sort_values(ascending=False)
    
    print("\nCURRENT MODEL FEATURES:")
    print("-" * 30)
    for feature in current_features:
        if feature in correlations:
            corr = correlations[feature]
            print(f"{feature:<20} {corr:.3f}")
    
    # Get available features not currently used
    future_data = pd.read_csv("../data/future_unseen_examples.csv", nrows=1)
    available_features = list(future_data.columns)
    
    unused_features = [f for f in available_features 
                      if f not in current_features and f in correlations]
    
    print("\nBEST UNUSED FEATURES:")
    print("-" * 30)
    
    # Sort unused features by correlation strength
    unused_corrs = [(f, correlations[f]) for f in unused_features]
    unused_corrs.sort(key=lambda x: abs(x[1]), reverse=True)
    
    # Show top 5
    for i, (feature, corr) in enumerate(unused_corrs[:5], 1):
        print(f"{i}. {feature:<18} {corr:.3f}")
    
    # Show top 3 recommendations (dynamic based on data)
    print("\nRECOMMENDATIONS:")
    print("-" * 30)
    print("Add these 3 features to improve the model:")
    
    # Print top 3 dynamically with correlations
    for i, (feature, corr) in enumerate(unused_corrs[:3], 1):
        print(f"{i}. '{feature}' (correlation: {corr:.3f})")
    
    # Save simple results
    results = {
        'top_3_features': [f for f, _ in unused_corrs[:3]],
        'correlations': {f: float(corr) for f, corr in unused_corrs[:3]},
        'date': pd.Timestamp.now().isoformat()
    }
    
    output_file = Path("./feature_recommendations.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
