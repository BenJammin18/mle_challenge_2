# Sound Realty House Price API

A REST API for predicting house prices in the Seattle area using machine learning.

## Quick Start

### 1. Prerequisites
- **Local**: Python 3.8+
- **Docker**: Docker and Docker Compose
- **Kubernetes**: kubectl and minikube

### 2. Deploy the API

Navigate to the project directory and run:

```bash
cd src
./deploy.sh [MODE] [METHOD]
```

**Options:**
- `MODE`: `dev` (default) or `prod`
- `METHOD`: `local` (default), `docker`, or `k8s`

**Examples:**
```bash
./deploy.sh                    # Development mode locally
./deploy.sh prod docker        # Production mode with Docker
./deploy.sh dev k8s           # Development mode on Kubernetes
```

The API will be available at: **http://localhost:5005**

### 3. Test the API

```bash
./deploy.sh [MODE] [METHOD] test
```

### 4. Stop the API

```bash
./deploy.sh [MODE] [METHOD] stop
```

## API Usage

### Health Check
```bash
curl http://localhost:5005/health
```

### Predict House Price
```bash
curl -X POST http://localhost:5005/predict \
  -H "Content-Type: application/json" \
  -d '{
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft_living": 1800,
    "sqft_lot": 5000,
    "floors": 1,
    "sqft_above": 1800,
    "sqft_basement": 0,
    "zipcode": "98103"
  }'
```

**Response:**
```json
{
  "status": "success",
  "predicted_price": 537100.0,
  "currency": "USD",
  "zipcode": "98103"
}
```

### API Documentation
Interactive documentation is available at:
- **Development**: http://localhost:5005/apidocs
- **Production**: http://localhost:5005/apidocs

## Deployment Methods

### Local Development
- Runs directly with Python
- Best for development and testing
- Automatic virtual environment setup

### Docker
- Containerized deployment
- Includes monitoring with Prometheus and Grafana
- Good for production-like testing

### Kubernetes
- Scalable deployment on minikube
- Production-ready configuration
- Automatic port forwarding setup

## Monitoring (Prod only)

When using prod deployment, monitoring tools are available:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Production Features

- **Full-stack monitoring**: In production mode (`./deploy.sh prod docker` or `./deploy.sh prod k8s`), Prometheus and Grafana are automatically started and integrated for metrics and dashboards.
- **Automatic port management**: The deployment script ensures that only the processes it starts are stopped, and ports are freed up cleanly when you run `./deploy.sh prod [docker|k8s|local] stop`.
- **Kubernetes and Docker support**: You can deploy to either Docker Compose or Minikube-based Kubernetes with a single script and consistent interface.
- **Graceful cleanup**: Stopping a deployment will only terminate the relevant containers, port-forwards, or Python processes, without affecting unrelated services on your system.
- **Nginx sample config**: An example `nginx.conf` is included in `src/` as a reference for reverse proxying or load balancing, but it is not used by the deployment script or containers by default. You can adapt it for your own production needs if desired.

## Project Structure

```
src/
├── deploy.sh              # Main deployment script
├── app_development.py     # Development API server
├── app_production.py      # Production API server
├── docker-compose.yml     # Docker configuration
├── k8s-development.yml    # Kubernetes dev config
├── k8s-production.yml     # Kubernetes prod config
└── requirements.txt       # Python dependencies

../model/
├── model.pkl             # Trained ML model
└── model_features.json   # Required features

../data/
├── zipcode_demographics.csv  # Demographics data
└── future_unseen_examples.csv # Test examples
```

## Troubleshooting

**Kubernetes issues:**
- Ensure minikube is running: `minikube start`
- Check pod status: `kubectl get pods`

**Docker issues:**
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs`

**Local issues:**
- Check if port 5005 is in use
- Verify Python dependencies are installed
