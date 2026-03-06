# Local Deployment with Minikube

The Minikube deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves a single instance of each of the two microservices comprising the application. Unlike the Docker Compose deployment, it uses PostgreSQL (instead of SQLite) as the master data database. In addition, it includes:
- PostgreSQL server as the RDBMS for the master data service
- Redis for pub/sub notifications between the master data service and query service instances
- Nginx Ingress for routing external traffic to the microservices
- Prometheus and Grafana for metrics and dashboards


## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/) installed and running
- `kubectl` configured to use the Minikube context
- The Minikube Ingress addon enabled (see below)


## Deployment

**Enable the Ingress addon** (one-time setup):
```
minikube addons enable ingress
```

**All manifests must be applied from the `dev-ops/minikube/` directory.** The ordering below is required because later resources depend on earlier ones (namespace must exist before other resources, infrastructure services before application services):

```
kubectl apply -f namespace.yml
kubectl apply -f ingress.yml
kubectl apply -f postgres.yml
kubectl apply -f redis.yml
kubectl apply -f prometheus-http-discovery.yml
kubectl apply -f prometheus-server.yml
kubectl apply -f grafana.yml
kubectl apply -f master-data-service.yml
kubectl apply -f query-service.yml
```

**Verify the deployment:**
```
kubectl get pods -n city-navigator
kubectl get ingress -n city-navigator
```

Wait until all pods show `Running` status before accessing the application.


## Teardown

Resources should be deleted in reverse dependency order:

```
kubectl delete -f query-service.yml
kubectl delete -f master-data-service.yml
kubectl delete -f grafana.yml
kubectl delete -f prometheus-server.yml
kubectl delete -f prometheus-http-discovery.yml
kubectl delete -f redis.yml
kubectl delete -f postgres.yml
kubectl delete -f ingress.yml
kubectl delete -f namespace.yml
```
