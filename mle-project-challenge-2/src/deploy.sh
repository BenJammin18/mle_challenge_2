#!/bin/bash
# Deploy script for SoundRealty API 
# Usage: ./deploy.sh [MODE] [METHOD] [ACTION]
#
# MODE:    dev | prod        (default: dev)
# METHOD:  local | docker | k8s   (default: local)  
# ACTION:  status | stop | test   (optional)

set -e
MODE=${1:-dev}
METHOD=${2:-local}
ACTION=${3:-}

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SRC_DIR="$PROJECT_DIR/src"
DATA_DIR="$PROJECT_DIR/data"
MODEL_DIR="$PROJECT_DIR/model"

# Check prerequisites
check_prereqs() {
  case "$1" in
    docker) command -v docker >/dev/null || { echo "Error: Docker not found"; exit 1; } ;;
    k8s) command -v kubectl >/dev/null || { echo "Error: kubectl not found"; exit 1; } ;;
    local) command -v python3 >/dev/null || { echo "Error: python3 not found"; exit 1; } ;;
  esac
}

# Show status
show_status() {
  case "$METHOD" in
    docker) docker-compose -f "$SRC_DIR/docker-compose.yml" ps ;;
    k8s) kubectl get pods -l app=api-${MODE} ;;
    local) pgrep -fl "app_${MODE}.py" || echo "No local process running" ;;
  esac
}

# Stop services
stop_services() {
  case "$METHOD" in
    docker) 
      docker-compose -f "$SRC_DIR/docker-compose.yml" down
      echo "Docker services stopped"
      ;;
    k8s)
      if [ "$MODE" = "dev" ]; then
        kubectl delete -f "$SRC_DIR/k8s-development.yml" >/dev/null 2>&1 || true
      else
        kubectl delete -f "$SRC_DIR/k8s-production.yml" >/dev/null 2>&1 || true
      fi
      pkill -f "kubectl port-forward.*api-${MODE}" 2>/dev/null || true
      echo "Kubernetes deployment stopped"
      ;;
    local)
      pkill -f "app_${MODE}.py" || true
      rm -f "/tmp/soundrealty_${MODE}.pid"
      echo "Local process stopped"
      ;;
  esac
}

# Test API endpoints
test_api() {
  if [ "$METHOD" = "k8s" ]; then
    kubectl port-forward svc/api-${MODE} 5005:5005 >/dev/null 2>&1 &
    PORT_FORWARD_PID=$!
    sleep 3
    trap "kill $PORT_FORWARD_PID 2>/dev/null || true" EXIT
  elif [ "$METHOD" = "docker" ]; then
    echo "Waiting for Docker containers to be ready..."
    sleep 5
  fi
  
  echo "Testing health endpoint..."
  curl -s http://localhost:5005/health || echo "Health check failed"
  echo
  echo "Testing prediction endpoint..."
  curl -s -X POST http://localhost:5005/predict \
    -H 'Content-Type: application/json' \
    -d '{"bedrooms":3,"bathrooms":2,"sqft_living":1800,"sqft_lot":5000,"floors":1,"sqft_above":1800,"sqft_basement":0,"zipcode":"98103"}' || echo "Prediction failed"
  echo
}

# Handle actions
case "$ACTION" in
  status) show_status; exit 0 ;;
  stop) stop_services; exit 0 ;;
  test) test_api; exit 0 ;;
esac

check_prereqs "$METHOD"

# Deploy based on method
case "$METHOD" in
  k8s)
    minikube status >/dev/null 2>&1 || { echo "Error: Minikube not running"; exit 1; }
    # Switch Docker context to minikube
    eval $(minikube docker-env)
    docker build -f "$SRC_DIR/Dockerfile" -t api-${MODE}:latest --target=${MODE} "$PROJECT_DIR" --quiet
    if [ "$MODE" = "dev" ]; then
      kubectl apply -f "$SRC_DIR/k8s-development.yml" >/dev/null
    else
      kubectl apply -f "$SRC_DIR/k8s-production.yml" >/dev/null
    fi
    kubectl wait --for=condition=ready pod -l app=api-${MODE} --timeout=60s >/dev/null
    kubectl port-forward svc/api-${MODE} 5005:5005 >/dev/null 2>&1 &
    # Reset Docker context to default after k8s build
    eval $(minikube docker-env -u)
    echo "Kubernetes deployment complete. API available at http://localhost:5005"
    ;;
  docker)
    # Ensure Docker context is set to Docker Desktop (not minikube)
    eval $(minikube docker-env -u)
    SERVICE="api-$MODE"
    docker-compose -f "$SRC_DIR/docker-compose.yml" up --build -d $SERVICE
    echo "Docker deployment complete. API available at http://localhost:5005"
    ;;
  local)
    cd "$SRC_DIR"
    python3 -m venv venv >/dev/null 2>&1 && source venv/bin/activate
    pip install -r requirements.txt >/dev/null 2>&1
    if [ "$MODE" = "dev" ]; then
      script="app_development.py"
      echo "Running development server..."
    else
      script="app_production.py"
      echo "Running production server..."
    fi
    python $script &
    echo $! > "/tmp/soundrealty_${MODE}.pid"
    echo "Local deployment complete. API available at http://localhost:5005"
    ;;
esac
