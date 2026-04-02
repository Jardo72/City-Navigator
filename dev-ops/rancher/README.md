# Deployment with Rancher

This deployment targets a Rancher-managed Kubernetes cluster. It covers both microservices and their infrastructure dependencies (PostgreSQL, Redis), an Ingress for external access, and optional integration with Rancher Monitoring for metrics and dashboards.

Compared to the Docker Compose and Minikube deployments, this deployment has the following notable differences:
- Prometheus and Grafana are not deployed as standalone resources. Instead, Rancher's built-in monitoring stack (kube-prometheus-stack / Rancher Monitoring) provides both. The `servicemonitor.yml` manifest provisions `ServiceMonitor` CRDs that the Prometheus Operator uses to discover scrape targets.
- The Prometheus HTTP Service Discovery service is not used. Service discovery is handled natively by the Prometheus Operator via the `ServiceMonitor` CRDs.
- Grafana dashboards are deployed as ConfigMaps to the `cattle-monitoring-system` namespace, where Rancher's Grafana sidecar picks them up automatically.


## Prerequisites

- A Rancher-managed Kubernetes cluster with `kubectl` configured to point at it
- The nginx Ingress controller installed in the cluster
- Rancher Monitoring (kube-prometheus-stack) installed — required for `servicemonitor.yml` and `grafana-dashboards.yml`


## Secrets

Credentials are not stored in the YAML manifests in this repository. Instead, a Kubernetes Secret must be created manually in the cluster before deploying. The commands below show the required structure — **replace the placeholder values with real credentials before running**:

```
kubectl create secret generic postgres-credentials \
  --namespace city-navigator \
  --from-literal=username=dbuser \
  --from-literal=password=changeme
```

The `postgres-credentials` Secret is referenced by `postgres.yml`, `data-importer.yml`, and `master-data-service.yml`. All three must be deployed after the Secret exists.

> **Note:** Redis does not require authentication in the current deployment — the Redis container runs without a password and the application connects without credentials.


## Local Hostname Setup

The Ingress is configured for the hostname `city-navigator.jch`. To access the application, map the Ingress IP address to this hostname.

Get the Ingress IP address:
```
kubectl get ingress -n city-navigator
```

Then add the following entry to your `/etc/hosts` file (on Windows: `C:\Windows\System32\drivers\etc\hosts`):
```
<ingress-ip>  city-navigator.jch
```


## Deployment

The manifests must be applied in the following order. Later resources depend on earlier ones (the namespace must exist before any other resource, and the database must be populated before the application services start).

**The namespace can be created either via the Rancher UI or by applying the manifest:**
```
kubectl apply -f namespace.yml
```

**Create the Secret** (see [Secrets](#secrets) for the required command — use real credentials, not the placeholders shown there).

**Then apply the remaining manifests in order:**
```
kubectl apply -f logging-configurations.yml
kubectl apply -f postgres.yml
kubectl apply -f redis.yml
kubectl apply -f data-importer.yml
kubectl wait --for=condition=complete job/data-importer -n city-navigator --timeout=120s
kubectl apply -f master-data-service.yml
kubectl apply -f query-service.yml
kubectl apply -f ingress.yml
```

The `data-importer` is a Kubernetes Job that populates the PostgreSQL database with the city plan data. It uses an init container to wait until PostgreSQL is ready before running. The master data service and query service must only be started after the Job has completed successfully.

> **Re-running the data importer:** If the database loses its data (e.g. after a PostgreSQL pod restart), you need to re-run the data-importer Job. Kubernetes Jobs have immutable fields, so `kubectl apply` on an existing Job will fail with an immutable field error. Delete the completed Job first, then re-apply:
> ```
> kubectl delete job data-importer -n city-navigator
> kubectl apply -f data-importer.yml
> kubectl wait --for=condition=complete job/data-importer -n city-navigator --timeout=120s
> ```

**Monitoring and dashboards** require Rancher Monitoring to be installed. If it is available, apply the remaining manifests:
```
kubectl apply -f servicemonitor.yml
kubectl apply -f grafana-dashboards.yml
```

Note: `grafana-dashboards.yml` deploys ConfigMaps to the `cattle-dashboards` namespace, which is where the Grafana sidecar in Rancher Monitoring watches for custom dashboards. If Rancher Monitoring is not installed, that namespace does not exist and this manifest will fail. `servicemonitor.yml` requires the `monitoring.coreos.com/v1` CRD, which is also provided by Rancher Monitoring.


## Verification

```
kubectl get pods -n city-navigator
kubectl get jobs -n city-navigator
kubectl get ingress -n city-navigator
```

Wait until all pods show `Running` status and the data-importer Job shows `Complete` before accessing the application.


## Testing via Ingress

Once the hostname is mapped (see [Local Hostname Setup](#local-hostname-setup)), the following endpoints can be used to verify the deployment:

```
http://city-navigator.jch/api/query/means-of-transport
http://city-navigator.jch/api/query/stations
http://city-navigator.jch/api/query/lines
http://city-navigator.jch/api/query/journey-plan?start=Traisengasse&destination=Nordwestbahnstrasse
```


## Logging

The `logging-configurations.yml` manifest provisions two ConfigMaps — one for the master data service and one for the query service — each containing the Python logging configuration. The configuration files are mounted into the containers at `/usr/src/app/logging.yaml`.

In this deployment, logging is configured for console output only (stdout). Kubernetes captures stdout from all containers, so structured logs are accessible via `kubectl logs`. There is no file-based logging or Loki integration in this deployment.


## Grafana Dashboards

When Rancher Monitoring is available, the `grafana-dashboards.yml` manifest deploys three dashboards as ConfigMaps labeled `grafana_dashboard: '1'` to the `cattle-dashboards` namespace. The Grafana sidecar watches that namespace and picks them up automatically:

- **City Navigator - Overview** — high-level health across both services (availability, request rate, latency, error rate)
- **City Navigator - Query Service (per instance)** — per-endpoint, per-instance breakdown for use during load tests
- **City Navigator - Query Service (aggregated)** — the same panels aggregated across all query service instances

The dashboard JSON embeds a Prometheus datasource UID. If the UID does not match the datasource registered in Rancher's Grafana, open each dashboard after deployment, re-select the Prometheus datasource, and save.
