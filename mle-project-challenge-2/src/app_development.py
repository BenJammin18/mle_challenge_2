"""
Simple REST API for Sound Realty House Price Prediction
"""
import json
import pickle
import pandas as pd
from flask import Flask, request, jsonify
import os
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

# Global variables
model = None
model_features = None
demographics_data = None

def load_model_artifacts():
    """Load model and data on startup."""
    global model, model_features, demographics_data
    
    # Auto-detect paths (Docker vs local)
    if os.path.exists('./model/model.pkl'):
        model_path = './model/model.pkl'
        features_path = './model/model_features.json'
        demographics_path = './data/zipcode_demographics.csv'
    else:
        model_path = '../model/model.pkl'
        features_path = '../model/model_features.json'
        demographics_path = '../data/zipcode_demographics.csv'
    
    # Load everything
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(features_path, 'r') as f:
        model_features = json.load(f)
    demographics_data = pd.read_csv(demographics_path, dtype={'zipcode': str})
    demographics_data.set_index('zipcode', inplace=True)
    
    print(f"Model loaded with {len(model_features)} features")

def prepare_features(house_data):
    """Prepare features for prediction."""
    # Normalize data types (handle floats, strings, etc.)
    normalized_data = {}
    for key, value in house_data.items():
        if value is None:
            normalized_data[key] = 0
        elif key == 'zipcode':
            # Handle zipcode as string or float
            normalized_data[key] = str(int(float(value)))
        else:
            # Convert to appropriate numeric type
            try:
                float_val = float(value)
                normalized_data[key] = int(float_val) if float_val.is_integer() else float_val
            except (ValueError, TypeError):
                normalized_data[key] = 0
    
    # Get zipcode and demographics
    zipcode = normalized_data['zipcode']
    if zipcode not in demographics_data.index:
        raise ValueError(f"Zipcode {zipcode} not found in demographics data")
    
    # Combine house data with demographics
    zipcode_demographics = demographics_data.loc[zipcode].to_dict()
    house_features = {k: v for k, v in normalized_data.items() if k != 'zipcode'}
    combined_features = {**house_features, **zipcode_demographics}
    
    # Create DataFrame in correct order
    feature_df = pd.DataFrame([combined_features])
    feature_df = feature_df.reindex(columns=model_features, fill_value=0)
    
    return feature_df

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint.
    ---
    responses:
      200:
        description: API health status
    """
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    })

@app.route('/predict', methods=['POST'])
def predict_price():
    """Main prediction endpoint.
    ---
    parameters:
      - in: body
        name: house
        required: true
        schema:
          type: object
          properties:
            bedrooms:
              type: integer
            bathrooms:
              type: number
            sqft_living:
              type: integer
            sqft_lot:
              type: integer
            floors:
              type: number
            sqft_above:
              type: integer
            sqft_basement:
              type: integer
            zipcode:
              type: string
    responses:
      200:
        description: Predicted price
    """
    try:
        # Validate JSON request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        house_data = request.get_json()
        
        # Check for required zipcode
        if 'zipcode' not in house_data:
            return jsonify({"error": "Missing required field: zipcode"}), 400
        
        # Make prediction
        features_df = prepare_features(house_data)
        prediction = model.predict(features_df)[0]
        
        return jsonify({
            "predicted_price": float(prediction),
            "currency": "USD",
            "zipcode": house_data['zipcode'],
            "status": "success"
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/predict/simple', methods=['POST'])
def predict_price_simple():
    """Simplified prediction endpoint.
    ---
    parameters:
      - in: body
        name: house
        required: true
        schema:
          type: object
          properties:
            bedrooms:
              type: integer
            bathrooms:
              type: number
            sqft_living:
              type: integer
            sqft_lot:
              type: integer
            floors:
              type: number
            sqft_above:
              type: integer
            sqft_basement:
              type: integer
            zipcode:
              type: string
    responses:
      200:
        description: Predicted price (simple)
    """
    try:
        # Validate JSON request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        house_data = request.get_json()
        
        # Required core features
        core_features = ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                        'floors', 'sqft_above', 'sqft_basement', 'zipcode']
        
        # Check all required features
        missing = [f for f in core_features if f not in house_data]
        if missing:
            return jsonify({
                "error": f"Missing required features: {missing}",
                "required_features": core_features
            }), 400
        
        # Use only core features
        core_data = {k: house_data[k] for k in core_features}
        
        # Make prediction
        features_df = prepare_features(core_data)
        prediction = model.predict(features_df)[0]
        
        return jsonify({
            "predicted_price": float(prediction),
            "currency": "USD",
            "endpoint": "simple",
            "zipcode": house_data['zipcode'],
            "status": "success"
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@app.route('/features', methods=['GET'])
def get_required_features():
    """Return required features.
    ---
    responses:
      200:
        description: List of required features
    """
    return jsonify({
        "simple_endpoint_features": ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                                   'floors', 'sqft_above', 'sqft_basement', 'zipcode'],
        "model_features": model_features,
        "note": "Demographics are automatically added based on zipcode"
    })

# Load model on startup
load_model_artifacts()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)
