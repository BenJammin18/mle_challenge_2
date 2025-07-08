import requests
import sys

ENDPOINT = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5005/predict"
HEALTH_ENDPOINT = ENDPOINT.replace("/predict", "/health")

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

def test_health():
    r = requests.get(HEALTH_ENDPOINT)
    print(f"/health status: {r.status_code}")
    print(r.json())
    assert r.status_code == 200

def test_predict():
    r = requests.post(ENDPOINT, json=SAMPLE)
    print(f"/predict status: {r.status_code}")
    print(r.json())
    assert r.status_code == 200

if __name__ == "__main__":
    test_health()
    test_predict()
