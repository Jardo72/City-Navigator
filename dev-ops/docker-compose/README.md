# Local Development with Docker Compose
The Docker compose deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves a single instance of each of the two microservices comprising the application. In addition, it involves some additional containers:
- Nginx server serving as proxy. All REST requests sent to any of the two microservices are sent to the Nginx server. The server is configured with forwaring rules which direct each request to the proper microservice based on the resource path.
- PostgreSQL database used as the persistent store for the master data service.
- Data importer, a one-shot container that populates the PostgreSQL database with city plan data on startup.
- Redis serving as pub/sub messaging used to deliver notifications from the master data service to all query service instances.
- Prometheus server configured to scrape metrics from both microservices.
- Prometheus HTTP discovery service allowing Prometheus to discover all instances of the microservices, even in deployments with two or more instances of any of the service.
- Grafana configured to use the Prometheus server as a data source.


## Prerequisites

- Docker with the Compose plugin


## Starting and Stopping

Start all services:
```bash
docker compose up -d --wait
```

Docker Compose handles the startup ordering automatically: PostgreSQL starts first and becomes healthy, then the data importer runs and populates the database, and only then the master data service starts. The `--wait` flag makes the command block until all services have started successfully.

Stop all services:
```bash
docker compose down
```


## Service Dependencies

Docker Compose starts services in the order determined by their `depends_on` declarations. The diagram below shows the full dependency graph, including the condition type for each dependency (`service_healthy`, `service_completed_successfully`, or `service_started`).

![dependencies](./dependencies.png)

The most notable aspects of the startup ordering:
- The data importer waits until PostgreSQL passes its health check before running (`service_healthy`).
- The master data service waits until the data importer finishes successfully (`service_completed_successfully`), ensuring the database is populated before the service accepts requests.
- All other dependencies use `service_started`, meaning Docker Compose only waits for the container to be running, not for the application inside to be ready.


## Services and Ports

| Service | Host Port | Description |
|---|---|---|
| Nginx | 80 | Reverse proxy — entry point for the REST API |
| Prometheus | 9090 | Metrics scraping and query UI |
| Grafana | 3000 | Dashboards (admin / GrafanaSecret#37) |
| HTTP Service Discovery | 9099 | Prometheus HTTP SD endpoint |

PostgreSQL, Redis, the data importer, the two microservices, and Nginx are on an internal `service-network` and are not directly exposed to the host (except Nginx on port 80). Prometheus and Grafana share a separate `monitoring-network`.


## Nginx HTTP Router

Nginx serves as the single entry point for all REST API requests. The configuration is in [./nginx/nginx.conf](./nginx/nginx.conf). Routing rules:

| URL prefix | Forwarded to |
|---|---|
| `/city-navigator/api/master-data/` | `master-data-service:8000` |
| `/city-navigator/api/query/` | `query-service:8000` |


## Redis Pub/Sub

Redis is used exclusively for pub/sub notifications from the master data service to the query service. Whenever an entity is created, updated, or deleted in the master data database, a notification is published on the `city-navigator` channel. Each query service instance subscribes to this channel and applies incremental updates to its in-memory database.


## Prometheus Server

Configuration is in [./prometheus](./prometheus). Prometheus uses the HTTP Service Discovery service to discover scrape targets dynamically — both microservices register themselves with it on startup.


## Prometheus HTTP Service Discovery

A lightweight FastAPI service that maintains a registry of running microservice instances and exposes it in the format required by Prometheus HTTP SD. Both microservices register with it at startup. Exposed on host port 9099.


## Grafana

Grafana is pre-provisioned with a Prometheus data source and a City Navigator dashboard. The provisioning configuration is in [./grafana](./grafana). Default credentials: `admin` / `GrafanaSecret#37`.


## HTTP Access Logs

HTTP access logs for all three services (master-data-service, query-service, http-service-discovery) are written to the [./access-logs](./access-logs) directory, which is bind-mounted into each container. Log files are gitignored; see [./access-logs/README.md](./access-logs/README.md).
