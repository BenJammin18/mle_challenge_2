"""
Test script for Sound Realty House Price Prediction API
Demonstrates API usage with sample data from future_unseen_examples.csv
Supports both development and production environments
"""
import requests
import json
import pandas as pd
import sys
import numpy as np
import argparse
from datetime import datetime

# Default configuration
DEFAULT_URL = "http://localhost:5005"

# Test results tracking
results = {'passed': 0, 'failed': 0, 'irregular': 0, 'details': []}

def log(test_name, status, message=""):
    """Log test result"""
    results[status] += 1
    symbol = "PASS" if status == "passed" else "FAIL" if status == "failed" else "WARN"
    print(f"[{symbol}] {test_name}: {message}")
    results['details'].append((test_name, status, message))

def test_health():
    """Test API health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200 and response.json().get('status') == 'healthy':
            log("Health Check", "passed", "API is healthy")
            return True
        else:
            log("Health Check", "failed", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log("Health Check", "failed", f"Connection error: {e}")
        return False

def test_features():
    """Test /features endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/features", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'model_features' in data:
                log("Features Endpoint", "passed", f"{len(data['model_features'])} features available")
                return True
            else:
                log("Features Endpoint", "failed", "Missing model_features key")
                return False
        else:
            log("Features Endpoint", "failed", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log("Features Endpoint", "failed", f"Error: {e}")
        return False

def test_simple_prediction():
    """Test /predict/simple endpoint"""
    test_data = {
        "bedrooms": 3, "bathrooms": 2, "sqft_living": 1500,
        "sqft_lot": 5000, "floors": 1, "sqft_above": 1500,
        "sqft_basement": 0, "zipcode": 98103
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict/simple", json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            price = result.get('predicted_price', 0)
            if 50000 <= price <= 5000000:
                log("Simple Prediction", "passed", f"Price: ${price:,.2f}")
                return True
            else:
                log("Simple Prediction", "irregular", f"Price outside range: ${price:,.2f}")
                return False
        else:
            log("Simple Prediction", "failed", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log("Simple Prediction", "failed", f"Error: {e}")
        return False

def test_full_prediction():
    """Test /predict endpoint with CSV example"""
    try:
        examples = pd.read_csv('../data/future_unseen_examples.csv')
        house_data = examples.iloc[0].to_dict()
        response = requests.post(f"{BASE_URL}/predict", json=house_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            price = result.get('predicted_price', 0)
            if 50000 <= price <= 5000000:
                log("Full Prediction", "passed", f"Price: ${price:,.2f}")
                return True
            else:
                log("Full Prediction", "irregular", f"Price outside range: ${price:,.2f}")
                return False
        else:
            try:
                error_info = response.json()
                log("Full Prediction", "failed", f"HTTP {response.status_code}: {error_info}")
            except:
                log("Full Prediction", "failed", f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log("Full Prediction", "failed", f"Error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    try:
        # Test with missing required fields
        response = requests.post(f"{BASE_URL}/predict/simple", json={"bedrooms": 3}, timeout=10)
        if response.status_code == 400:
            log("Error Handling", "passed", "Correctly rejected invalid data")
            return True
        else:
            log("Error Handling", "failed", f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        log("Error Handling", "failed", f"Error: {e}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    total = results['passed'] + results['failed'] + results['irregular']
    print(f"Total Tests: {total}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Irregular: {results['irregular']}")
    
    if total > 0:
        success_rate = (results['passed'] / total) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    # Show failed and irregular tests
    if results['failed'] > 0 or results['irregular'] > 0:
        print("\nISSUES:")
        for test_name, status, message in results['details']:
            if status in ['failed', 'irregular']:
                symbol = "FAIL" if status == "failed" else "WARN"
                print(f"[{symbol}] {test_name}: {message}")
    
    print("="*50)
    
    if results['failed'] == 0:
        if results['irregular'] == 0:
            print("ALL TESTS PASSED!")
        else:
            print("Tests completed with some irregular results")
        return True
    else:
        print("Some tests failed")
        return False

def main():
    """Run all tests"""
    print("Sound Realty API Test Suite")
    print("="*50)
    
    # Run tests
    if not test_health():
        print("API not running. Start with: cd api && python app.py")
        sys.exit(1)
    
    test_features()
    test_simple_prediction()
    test_full_prediction()
    test_error_handling()
    
    # Print summary and exit
    success = print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
