# Prometheus HTTP Discovery Service

## Introduction

The Prometheus HTTP Discovery Service is a lightweight helper used in the Docker Compose deployment. It implements the [Prometheus HTTP service discovery](https://prometheus.io/docs/prometheus/latest/http_sd/) protocol, allowing Prometheus to dynamically learn which service instances to scrape for metrics — without requiring a static `scrape_configs` target list.

On startup, each Master Data Service and Query Service instance registers itself by posting its hostname to this service. Prometheus periodically polls the `/targets` endpoint and receives the current list of registered instances, grouped by service name, in the format Prometheus expects.

The service is implemented in Python using [FastAPI](https://fastapi.tiangolo.com/) and runs under Gunicorn with uvicorn workers. All registered targets are held in memory only and are lost on container restart.


## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `ACCESS_LOG` | no | `/proc/1/fd/1` | Path for the Gunicorn HTTP access log file. Defaults to stdout. |


## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/version` | Returns application name, version, Python version, and hostname |
| `POST` | `/target` | Registers a service instance as a Prometheus scrape target |
| `GET` | `/targets` | Returns all registered targets in Prometheus HTTP SD format |

### POST /target

Registers a service instance. Called by Master Data Service and Query Service instances on startup.

**Request body (JSON):**

| Field | Type | Description |
|---|---|---|
| `hostname` | string | Hostname (or `hostname:port`) of the registering instance |
| `service` | string | Service identifier, e.g. `master-data-service` or `query-service` |

Re-posting the same hostname for a service is idempotent — the entry is updated rather than duplicated.

### GET /targets

Returns registered targets in the format required by Prometheus HTTP service discovery. Prometheus is configured to poll this endpoint periodically.

**Response body (JSON array):**

```json
[
  {
    "targets": ["query-service-1:8000", "query-service-2:8000"],
    "labels": { "service": "query-service" }
  },
  {
    "targets": ["master-data-service:8000"],
    "labels": { "service": "master-data-service" }
  }
]
```

Each element in the array corresponds to one service. The `labels` object is attached by Prometheus to all time series scraped from the listed targets, making it possible to filter metrics by service in Grafana.
