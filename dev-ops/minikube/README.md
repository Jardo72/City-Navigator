# Local Deployment with Minikube

The Minikube deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves both microservices comprising the application. In addition, it also includes:
- PostgreSQL server as the RDBMS for the master data service
- Redis for pub/sub notifications between the master data service and query service instances
- Prometheus and Grafana for metrics and dashboards


## Prerequisites

- A local Kubernetes cluster — either [Minikube](https://minikube.sigs.k8s.io/) or Docker Desktop with Kubernetes enabled
- `kubectl` configured to point at the local cluster
- The nginx Ingress controller installed (see below)


## Local hostname setup

The Ingress is configured for the hostname `city-navigator.jch`. Add the following entry to your `/etc/hosts` file. On Windows, the hosts file resides in the `C:\Windows\System32\drivers\etc` directory.

With **minikube**, use `minikube ip` to get the cluster IP:
```
<minikube-ip>  city-navigator.jch
```

With **Docker Desktop** built-in Kubernetes, the cluster is always reachable at `localhost`:
```
127.0.0.1  city-navigator.jch
```


## Deployment

**Install the nginx Ingress controller** (one-time setup):

With **minikube**:
```
minikube addons enable ingress
```

With **Docker Desktop**:
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.0/deploy/static/provider/cloud/deploy.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
```

**All manifests must be applied from the `dev-ops/minikube/` directory.** The ordering below is required because later resources depend on earlier ones (namespace must exist before other resources, infrastructure before application services):

```
kubectl apply -f namespace.yml
kubectl apply -f ingress.yml
kubectl apply -f postgres.yml
kubectl apply -f redis.yml
kubectl apply -f prometheus-http-discovery.yml
kubectl apply -f prometheus-server.yml
kubectl apply -f grafana.yml
kubectl apply -f data-importer.yml
kubectl wait --for=condition=complete job/data-importer -n city-navigator --timeout=120s
kubectl apply -f master-data-service.yml
kubectl apply -f query-service.yml
```

The `data-importer` is a Kubernetes Job that populates the PostgreSQL database with the city plan data. It uses an init container to wait until PostgreSQL is ready before running. The master data service and query service should only be started after the Job has completed successfully:


**Verify the deployment:**
```
kubectl get pods -n city-navigator
kubectl get jobs -n city-navigator
kubectl get ingress -n city-navigator
```

Wait until all pods show `Running` status and the data-importer Job shows `Complete` before accessing the application.


## Teardown

Resources should be deleted in reverse dependency order:

```
kubectl delete -f query-service.yml
kubectl delete -f master-data-service.yml
kubectl delete -f data-importer.yml
kubectl delete -f grafana.yml
kubectl delete -f prometheus-server.yml
kubectl delete -f prometheus-http-discovery.yml
kubectl delete -f redis.yml
kubectl delete -f postgres.yml
kubectl delete -f ingress.yml
kubectl delete -f namespace.yml
```
