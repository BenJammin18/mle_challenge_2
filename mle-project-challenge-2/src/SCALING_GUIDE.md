# Scaling Guide

## Docker Compose
- Increase `replicas` by adding more API services in `docker-compose.yml`.
- Use a load balancer (e.g., NGINX) to distribute traffic.

## Kubernetes
- Edit `replicas` in `k8s-development.yml` or `k8s-production.yml`.
- Use `kubectl scale deployment api-dev --replicas=3` (or `api-prod`).
- Use Kubernetes Ingress for advanced routing and SSL.

## Monitoring
- Prometheus and Grafana are included for metrics and dashboards.
