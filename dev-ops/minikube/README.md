# Local Deployment with Minikube
The Minikube deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves a single instance of each of the two microservices comprising the application. In addition, it involves some additional containers:
- Postgres server serving as RDBMS for the master data service.
- Redis serving as pub/sub messaging used to deliver notifications from the master data service to all query service instances.

## Commands
Start the services:
```
kubectl apply -f postgres.yml
kubectl apply -f redis.yml
kubectl apply -f prometheus-http-discovery.yml
kubectl apply -f prometheus-server.yml
kubectl apply -f master-data-service.yml
kubectl apply -f query-service.yml
```

Stop the services:
```
kubectl delete -f query-service.yml
kubectl delete -f master-data-service.yml
kubectl delete -f prometheus-server.yml
kubectl delete -f prometheus-http-discovery.yml
kubectl delete -f redis.yml
kubectl delete -f postgres.yml
```
