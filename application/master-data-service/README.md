# City Navigator - Master Data Service

## Introduction

The Master Data Service is a REST API for managing public transport data: means of transport, stations, lines, and their itineraries (edges). It is intended for administrative use — creating, reading, updating, and deleting entities.

Whenever an entity is mutated, the service publishes a notification to a Redis pub/sub channel so that all Query Service instances can synchronise their in-memory databases.

The service is implemented in Python using [FastAPI](https://fastapi.tiangolo.com/) and [SQLAlchemy](https://www.sqlalchemy.org/), and runs under Gunicorn with uvicorn workers. It is instrumented with the Prometheus Python client and registers itself with an HTTP Service Discovery service on startup.


## Configuration

The service is configured entirely via environment variables.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | yes | — | SQLAlchemy database URL, e.g. `sqlite:////db/sqlite.db` or `postgresql+psycopg2://user:pass@host/db` |
| `REDIS_HOST` | yes | — | Hostname of the Redis server used for pub/sub notifications |
| `REDIS_PORT` | no | `6379` | Port of the Redis server |
| `REDIS_CHANNEL` | no | `city-navigator` | Redis pub/sub channel name |
| `PROMETHEUS_DISCOVERY_BASE_URL` | yes | — | Base URL of the HTTP Service Discovery service, e.g. `http://prometheus-http-discovery:8000` |
| `ROOT_PATH` | no | _(empty)_ | FastAPI root path; set when the service is behind a reverse proxy, e.g. `/city-navigator/api/master-data` |
| `API_DOC_ENABLED` | no | `NO` | Set to `YES`, `TRUE`, or `1` to enable the OpenAPI (`/docs`) and ReDoc (`/redoc`) endpoints. **Note:** enabling this disables Prometheus metrics scraping (the two features are mutually exclusive due to the multiprocess Prometheus setup). |
| `ACCESS_LOG` | no | `/proc/1/fd/1` | Path for the Gunicorn HTTP access log file. Defaults to stdout. |


## API Endpoints

All endpoints are relative to the service root. When deployed via Docker Compose, they are accessible through Nginx at `http://localhost/city-navigator/api/master-data<endpoint>`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/version` | Returns application name, version, Python version, and hostname |
| `GET` | `/means-of-transport` | List all means of transport |
| `GET` | `/means-of-transport/{uuid}` | Get a single means of transport by UUID |
| `POST` | `/means-of-transport` | Create a new means of transport |
| `PUT` | `/means-of-transport/{uuid}` | Update a means of transport |
| `DELETE` | `/means-of-transport/{uuid}` | Delete a means of transport |
| `GET` | `/stations` | List all stations |
| `GET` | `/station/{uuid}` | Get a single station by UUID |
| `POST` | `/station` | Create a new station |
| `PUT` | `/station/{uuid}` | Update a station |
| `DELETE` | `/station/{uuid}` | Delete a station |
| `GET` | `/lines` | List all lines (summary) |
| `GET` | `/line/{uuid}` | Get a single line with full itinerary by UUID |
| `POST` | `/line` | Create a new line with itinerary |
| `PUT` | `/line/{uuid}` | Update a line and its itinerary |
| `DELETE` | `/line/{uuid}` | Delete a line (cascades to its edges) |
| `GET` | `/metrics` | Prometheus metrics endpoint |

When `API_DOC_ENABLED` is active, interactive API documentation is available at `/docs` (Swagger UI) and `/redoc`.


## Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `master_data_service_http_requests_total` | Counter | Number of HTTP requests, labelled by `method` and `path` |
| `master_data_service_http_errors_total` | Counter | Number of HTTP errors, labelled by `method`, `path`, and `status_code` |
| `master_data_service_http_request_duration_seconds` | Histogram | Request duration in seconds, labelled by `method` and `path` |
