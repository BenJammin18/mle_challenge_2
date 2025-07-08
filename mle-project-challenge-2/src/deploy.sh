#!/bin/bash
# Unified deployment script for Sound Realty House Price API
# Usage: ./deploy.sh [dev|prod] [local|docker|k8s] [status|stop|test]

set -e
MODE=${1:-dev}
METHOD=${2:-local}
ACTION=${3:-}

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
SRC_DIR="$PROJECT_DIR/src"
DATA_DIR="$PROJECT_DIR/data"
MODEL_DIR="$PROJECT_DIR/model"

# Helper: check prerequisites
check_prereqs() {
  case "$1" in
    docker)
      command -v docker >/dev/null || { echo "Docker not found"; exit 1; }
      command -v docker-compose >/dev/null || { echo "docker-compose not found"; exit 1; }
      ;;
    k8s)
      command -v kubectl >/dev/null || { echo "kubectl not found"; exit 1; }
      ;;
    local)
      command -v python3 >/dev/null || { echo "python3 not found"; exit 1; }
      ;;
  esac
}

# Helper: status
show_status() {
  case "$METHOD" in
    docker)
      docker-compose -f "$SRC_DIR/docker-compose.yml" ps
      ;;
    k8s)
      kubectl get pods
      ;;
    local)
      pgrep -fl "app_${MODE}.py" || echo "No local process running"
      ;;
  esac
}

# Helper: stop
stop_services() {
  case "$METHOD" in
    docker)
      docker-compose -f "$SRC_DIR/docker-compose.yml" down
      ;;
    k8s)
      if [ "$MODE" = "dev" ]; then
        kubectl delete -f "$SRC_DIR/k8s-development.yml"
      else
        kubectl delete -f "$SRC_DIR/k8s-production.yml"
      fi
      ;;
    local)
      pkill -f "app_${MODE}.py" || true
      ;;
  esac
}

# Helper: test endpoints
run_tests() {
  echo "Testing /health..."
  curl -s http://localhost:5005/health || true
  echo
  echo "Testing /predict..."
  curl -s -X POST http://localhost:5005/predict -H 'Content-Type: application/json' -d '{"bedrooms":3,"bathrooms":2,"sqft_living":1800,"sqft_lot":5000,"floors":1,"sqft_above":1800,"sqft_basement":0,"zipcode":"98103"}' || true
  echo
}

# Main logic
case "$ACTION" in
  status)
    show_status
    exit 0
    ;;
  stop)
    stop_services
    exit 0
    ;;
  test)
    run_tests
    exit 0
    ;;
esac

check_prereqs "$METHOD"

if [ "$METHOD" = "k8s" ]; then
  # Ensure Minikube is running
  if ! minikube status >/dev/null 2>&1; then
    echo "Minikube is not running. Please start Minikube first."
    exit 1
  fi
  # Use Minikube Docker daemon
  eval $(minikube docker-env)
  # Build the correct image for k8s
  if [ "$MODE" = "dev" ]; then
    docker build -t api-dev:latest --target=dev "$SRC_DIR"
    kubectl apply -f "$SRC_DIR/k8s-development.yml"
  else
    docker build -t api-prod:latest --target=prod "$SRC_DIR"
    kubectl apply -f "$SRC_DIR/k8s-production.yml"
  fi
  # Restore original docker env
  eval $(minikube docker-env -u)
  echo "Kubernetes deployment complete."
  exit 0
fi

case "$METHOD" in
  docker)
    docker-compose -f "$SRC_DIR/docker-compose.yml" up --build -d
    ;;
  local)
    cd "$SRC_DIR"
    python3 -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python "app_${MODE}.py" &
    echo $! > "/tmp/soundrealty_${MODE}.pid"
    cd "$PROJECT_DIR"
    ;;
esac

echo "Deployment started in $MODE mode using $METHOD."
