# City Navigator - Query Service

## Introduction

The Query Service is a read-only REST API for passengers. It allows querying means of transport, stations, and lines, and searching for journey plans using Dijkstra's shortest-path algorithm.

Each instance of the service maintains its own in-memory SQLite database. On startup it fetches all data from the Master Data Service in parallel. A background thread then subscribes to a Redis pub/sub channel and applies incremental updates as the master data changes.

The service is implemented in Python using [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/), and runs under Gunicorn with uvicorn workers. It is instrumented with the Prometheus Python client and registers itself with an HTTP Service Discovery service on startup.


## Configuration

The service is configured entirely via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `MASTER_DATA_SERVICE_BASE_URL` | yes | — | Base URL of the Master Data Service, e.g. `http://master-data-service:8000` |
| `REDIS_HOST` | yes | — | Hostname of the Redis server used for pub/sub notifications |
| `REDIS_PORT` | no | `6379` | Port of the Redis server |
| `REDIS_CHANNEL` | no | `city-navigator` | Redis pub/sub channel name (must match the Master Data Service) |
| `PROMETHEUS_DISCOVERY_BASE_URL` | yes | — | Base URL of the HTTP Service Discovery service, e.g. `http://prometheus-http-discovery:8000` |
| `ROOT_PATH` | no | _(empty)_ | FastAPI root path; set when the service is behind a reverse proxy, e.g. `/city-navigator/api/query` |
| `API_DOC_ENABLED` | no | `NO` | Set to `YES`, `TRUE`, or `1` to enable the OpenAPI (`/docs`) and ReDoc (`/redoc`) endpoints. **Note:** enabling this disables Prometheus metrics scraping. |
| `ACCESS_LOG` | no | `/proc/1/fd/1` | Path for the Gunicorn HTTP access log file. Defaults to stdout. |


## API Endpoints

All endpoints are relative to the service root. When deployed via Docker Compose, they are accessible through Nginx at `http://localhost/city-navigator/api/query<endpoint>`.

| Method | Path | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/version` | — | Returns application name, version, Python version, and hostname |
| `GET` | `/means-of-transport` | — | List all means of transport |
| `GET` | `/stations` | `filter` (optional) | List stations, optionally filtered by name. Supports `*` as wildcard, e.g. `filter=S*` |
| `GET` | `/station` | `name` (required) | Get a single station by exact name |
| `GET` | `/lines` | `means_of_transport` (optional) | List lines, optionally filtered by means of transport identifier |
| `GET` | `/line` | `label` (required) | Get a single line with full itinerary by label |
| `GET` | `/journey-plan` | `start`, `destination` (both required) | Find the shortest journey between two stations by name |
| `GET` | `/metrics` | — | Prometheus metrics endpoint |

When `API_DOC_ENABLED` is active, interactive API documentation is available at `/docs` (Swagger UI) and `/redoc`.


## Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `query_service_http_requests_total` | Counter | Number of HTTP requests, labelled by `method` and `path` |
| `query_service_http_errors_total` | Counter | Number of HTTP errors, labelled by `method`, `path`, and `status_code` |
| `query_service_http_request_duration_seconds` | Histogram | Request duration in seconds, labelled by `method` and `path` |
| `query_service_notification_errors_total` | Counter | Number of master data notifications that failed to be applied, labelled by `event_type` and `entity` |
