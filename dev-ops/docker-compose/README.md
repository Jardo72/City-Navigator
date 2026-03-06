# Local Development with Docker Compose
The Docker compose deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves a single instance of each of the two microservices comprising the application. In addition, it involves some additional containers:
- Nginx server serving as proxy. All REST requests sent to any of the two microservices are sent to the Nginx server. The server is configured with forwaring rules which direct each request to the proper microservice based on the resource path.
- Redis serving as pub/sub messaging used to deliver notifications from the master data service to all query service instances.
- Prometheus server configured to scrape metrics from both microservices.
- Prometheus HTTP discovery service allowing Prometheus to discover all instances of the microservices, even in deployments with two or more instances of any of the service.
- Grafana configured to use the Prometheus server as a data source.


## Prerequisites

- Docker with the Compose plugin
- `sqlite3` CLI (for initial database setup)


## Initial Setup

The SQLite database must be created and populated before starting the application for the first time. Run the following commands from the repository root:

**Create the database schema:**
```bash
sqlite3 dev-ops/docker-compose/data/sqlite.db \
    < application/postgres/init-scripts/create-schema.sql
```

**Import the city plan data:**
```bash
cd application/data-importer
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/main.py city-plan.json "sqlite:///../../dev-ops/docker-compose/data/sqlite.db"
deactivate
cd ../..
```

This needs to be done only once. The database file is persisted in the [./data](./data) directory (bind-mounted into the master-data-service container at `/db`). The file is gitignored; see [./data/README.md](./data/README.md).


## Starting and Stopping

Start all services (waits until healthy):
```bash
docker compose up -d --wait
```

Stop all services:
```bash
docker compose down
```


## Services and Ports

| Service | Host Port | Description |
|---|---|---|
| Nginx | 80 | Reverse proxy — entry point for the REST API |
| Prometheus | 9090 | Metrics scraping and query UI |
| Grafana | 3000 | Dashboards (admin / GrafanaSecret#37) |
| HTTP Service Discovery | 9099 | Prometheus HTTP SD endpoint |

Redis, the two microservices, and Nginx are on an internal `service-network` and are not directly exposed to the host (except Nginx on port 80). Prometheus and Grafana share a separate `monitoring-network`.


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
