# Sound Realty House Price Prediction API

REST API service for predicting house prices in the Seattle area using machine learning.

## Features

- **Full Prediction Endpoint** (`/predict`): Accepts all house features from `future_unseen_examples.csv`
- **Simple Prediction Endpoint** (`/predict/simple`): Accepts only core features required by the model
- **Automatic Demographics Integration**: Automatically adds demographic data based on zipcode
- **Docker Support**: Fully containerized for easy deployment and scaling
- **Health Monitoring**: Built-in health check endpoint
- **Error Handling**: Comprehensive validation and error responses

## Quick Start

### 1. Train the Model (if not already done)
```bash
# From the project root directory
conda env create -f conda_environment.yml
conda activate housing

# Train the model
python create_model.py
```

### 2. Run with Docker (Recommended)

#### Option A: Using Docker Compose (Recommended)
```bash
# From the api directory
cd api
docker-compose up --build
```

#### Option B: Using Docker Run (Manual Volume Mounting)
```bash
# From the api directory
cd api

# Build the image
docker build -t house-price-api .

# Run with proper volume mounts for model and data files
docker run -p 5005:5005 \
  -v "$(pwd)/../data:/app/data" \
  -v "$(pwd)/../model:/app/model" \
  house-price-api
```

**Important**: The `docker run` command requires manual volume mounting of the `data` and `model` directories. Docker Compose handles this automatically via the `docker-compose.yml` configuration.

### 3. Run Locally (Development)
```bash
# From the api directory
cd api
pip install -r requirements.txt

# Run the Flask app
python app.py
```

### 4. Test the API
```bash
# From the api directory
python test_api.py
```

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the API and model loading status.

### Full Prediction
```
POST /predict
Content-Type: application/json

{
  "bedrooms": 4,
  "bathrooms": 2.5,
  "sqft_living": 2220,
  "sqft_lot": 6380,
  "floors": 1.5,
  "waterfront": 0,
  "view": 0,
  "condition": 4,
  "grade": 8,
  "sqft_above": 1660,
  "sqft_basement": 560,
  "yr_built": 1931,
  "yr_renovated": 0,
  "zipcode": "98115",
  "lat": 47.6974,
  "long": -122.313,
  "sqft_living15": 950,
  "sqft_lot15": 6380
}
```

### Simple Prediction (Bonus Feature)
```
POST /predict/simple
Content-Type: application/json

{
  "bedrooms": 4,
  "bathrooms": 2.5,
  "sqft_living": 2220,
  "sqft_lot": 6380,
  "floors": 1.5,
  "sqft_above": 1660,
  "sqft_basement": 560,
  "zipcode": "98115"
}
```

### Feature Information
```
GET /features
```
Returns information about required features for each endpoint.

## Response Format

```json
{
  "predicted_price": 450000.00,
  "currency": "USD",
  "model_version": "1.0",
  "features_used": ["bedrooms", "bathrooms", ...],
  "zipcode": "98115",
  "status": "success"
}
```

## Project Structure

```
mle-project-challenge-2/
├── api/                    # API service directory
│   ├── app.py             # Flask REST API
│   ├── test_api.py        # API test suite
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Container configuration
│   ├── docker-compose.yml # Docker orchestration
│   └── README.md          # API documentation
├── data/                  # Training and test data
├── model/                 # Trained model artifacts
├── create_model.py        # Model training script
└── conda_environment.yml  # Conda environment
```

## Scaling Considerations

### Horizontal Scaling
- The API is stateless and can be scaled horizontally
- Use load balancers (nginx, HAProxy) to distribute requests
- Deploy multiple containers with different ports

### Model Updates
- Models are loaded at startup from the `../model` directory
- To update the model:
  1. Train new model with `python create_model.py` (from project root)
  2. Replace model files in the container
  3. Restart the service (or implement hot-reloading)

### Production Deployment
- Use `gunicorn` with multiple workers (included in Dockerfile)
- Set up health checks and monitoring
- Use environment variables for configuration
- Consider using Kubernetes for orchestration

## Example Usage with curl

```bash
# Health check
curl http://localhost:5000/health

# Make a prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft_living": 1800,
    "sqft_lot": 7500,
    "floors": 2,
    "waterfront": 0,
    "view": 0,
    "condition": 3,
    "grade": 7,
    "sqft_above": 1200,
    "sqft_basement": 600,
    "yr_built": 1980,
    "yr_renovated": 0,
    "zipcode": "98115",
    "lat": 47.69,
    "long": -122.29,
    "sqft_living15": 1560,
    "sqft_lot15": 7500
  }'
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful prediction
- `400`: Bad request (missing fields, invalid data)
- `500`: Internal server error

Error responses include descriptive messages:
```json
{
  "error": "Missing required fields: ['zipcode']"
}
```

## Architecture

```
Client Request → Flask API → Feature Preparation → Model Prediction → JSON Response
                     ↓
               Demographics Lookup (automatic)
```

The service automatically:
1. Validates input data
2. Looks up demographic data by zipcode
3. Combines house features with demographics
4. Formats features for the ML model
5. Returns prediction with metadata

## Troubleshooting

### Docker Run vs Docker Compose

**Issue**: `docker run` fails with "Model files not found" error.

**Cause**: When using `docker run` directly, the model and data files from the host machine are not accessible inside the container.

**Solution**: Use volume mounting with `docker run`:
```bash
# Correct way to run with Docker
docker run -p 5005:5005 \
  -v "$(pwd)/../data:/app/data" \
  -v "$(pwd)/../model:/app/model" \
  house-price-api
```

**Why Docker Compose works**: The `docker-compose.yml` file automatically mounts the required volumes:
```yaml
volumes:
  - ../data:/app/data
  - ../model:/app/model
```

### Model Files Not Found

If you get errors about missing model files:
1. Ensure you've trained the model first: `python create_model.py`
2. Check that `model/` directory exists in the project root
3. Verify the model files are present: `ls -la ../model/`

### Port Already in Use

If port 5005 is already in use:
```bash
# Kill any existing processes on port 5005
lsof -ti:5005 | xargs kill -9

# Or use a different port
docker run -p 5006:5005 house-price-api
```
