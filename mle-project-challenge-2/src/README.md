# Sound Realty House Price API

## Overview
This project provides a robust, minimal, and unified deployment for the Sound Realty House Price Prediction API. All code and configuration now reside in the `src/` directory. You can deploy in development or production mode, and choose between local, Docker, or Kubernetes deployment—all with a single script.

## Directory Structure
```
src/
  app_development.py      # Flask API (development)
  app_production.py       # Flask API (production)
  requirements.txt        # Python dependencies
  docker-compose.yml      # Docker Compose config
  nginx.conf              # NGINX reverse proxy config
  prometheus.yml          # Prometheus config
  k8s-development.yml    # Kubernetes manifest (dev)
  k8s-production.yml     # Kubernetes manifest (prod)
  deploy.sh               # Unified deployment script
  test_api.py             # Unified API test script (use this, test_api_unified.py is obsolete)

data/
  kc_house_data.csv       # Main dataset
  zipcode_demographics.csv# Demographics
  future_unseen_examples.csv # Test data

model/
  model.pkl               # Trained model
  model_features.json     # Model features
  model_evaluation.json   # Model evaluation

util/
  feature_eval.py         # Feature evaluation script
  feature_recommendations.json # Feature recommendations
```

## Deployment

### Prerequisites
- Python 3.8+
- Docker & Docker Compose (for Docker method)
- kubectl (for Kubernetes method)

### Usage
From the project root:

```
cd src
./deploy.sh [dev|prod] [local|docker|k8s] [status|stop|test]
```
- `dev` or `prod`: Choose API mode (default: dev)
- `local`, `docker`, or `k8s`: Choose deployment method (default: local)
- `status`, `stop`, `test`: Optional actions

#### Examples
- Start dev API locally: `./deploy.sh dev local`
- Start prod API in Docker: `./deploy.sh prod docker`
- Start dev API on Kubernetes: `./deploy.sh dev k8s`
- Check status: `./deploy.sh dev docker status`
- Stop services: `./deploy.sh prod k8s stop`
- Test endpoints: `./deploy.sh dev local test`

## API Documentation
- Swagger UI available at: `http://localhost:5005/docs` (dev) or `http://localhost:5006/docs` (prod)

## Monitoring & Observability
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **Grafana**: [http://localhost:3000](http://localhost:3000)

### Grafana & Prometheus Integration
- Prometheus is configured in `src/prometheus.yml` and scrapes both dev and prod API endpoints.
- Grafana default login: `admin` / `admin`

#### Connect Prometheus as a Data Source
1. Open Grafana in your browser.
2. Go to **Configuration > Data Sources**.
3. Click **Add data source** and select **Prometheus**.
4. Set URL to `http://prometheus:9090` (for Docker) or `http://localhost:9090` (for local).
5. Click **Save & Test**.

#### Import a Dashboard
1. Go to **Create > Import**.
2. Enter a dashboard ID or upload a JSON file.
3. Select Prometheus as the data source.
4. Click **Import**.

- Prometheus and Grafana are started by default in Docker Compose.
- For custom dashboards, see [Grafana Dashboards](https://grafana.com/grafana/dashboards/).

## Scaling Guide

### Docker Compose
- Increase `replicas` by adding more API services in `docker-compose.yml`.
- Use a load balancer (e.g., NGINX) to distribute traffic.

### Kubernetes
- Edit `replicas` in `k8s-development.yml` or `k8s-production.yml`.
- Use `kubectl scale deployment api-dev --replicas=3` (or `api-prod`).
- Use Kubernetes Ingress for advanced routing and SSL.

### Monitoring
- Prometheus and Grafana are included for metrics and dashboards.

## Notes
- All paths in configs/scripts reference `src/`.
- Remove the old `api/` directory after verifying migration.
- All environment, scaling, and monitoring instructions are now in this README.
- `test_api_unified.py` is obsolete; use `test_api.py` for all endpoint tests.
