import requests
import time

URL = "http://localhost:5005/predict"
SAMPLE = {
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft_living": 1800,
    "sqft_lot": 5000,
    "floors": 1,
    "sqft_above": 1800,
    "sqft_basement": 0,
    "zipcode": "98103"
}

for i in range(100):
    r = requests.post(URL, json=SAMPLE)
    print(f"Request {i+1}: {r.status_code} {r.json()}")
    time.sleep(0.1)
