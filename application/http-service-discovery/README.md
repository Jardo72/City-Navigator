# Prometheus HTTP Discovery Service

## Introduction

The Prometheus HTTP Discovery Service is a lightweight helper used in the Docker Compose deployment. It implements the [Prometheus HTTP service discovery](https://prometheus.io/docs/prometheus/latest/http_sd/) protocol, allowing Prometheus to dynamically learn which service instances to scrape for metrics — without requiring a static `scrape_configs` target list.

On startup, each Master Data Service and Query Service instance registers itself by posting its hostname to this service. Each instance then continues to re-register periodically as a heartbeat. Prometheus periodically polls the `/targets` endpoint and receives the current list of registered instances, grouped by service name, in the format Prometheus expects.

Entries that have not been refreshed within the configurable stale threshold (default: 75 seconds, controlled by `STALE_TARGET_THRESHOLD_SECONDS`) are considered stale and are automatically removed from the registry. This ensures that instances which have stopped or crashed are eventually dropped from the Prometheus scrape targets without requiring a manual intervention or a service restart.

The service is implemented in Python using [FastAPI](https://fastapi.tiangolo.com/) and runs under Gunicorn with uvicorn workers. All registered targets are held in memory only and are lost on container restart. Structured JSON logging is provided by [python-json-logger](https://github.com/madzak/python-json-logger); the logging configuration is loaded from a YAML file (see `LOG_CONFIG` below), with support for `${HOSTNAME}` substitution to produce per-instance log files.


## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `STALE_TARGET_THRESHOLD_SECONDS` | no | `75` | Number of seconds without a heartbeat after which a registered target is considered stale and removed from the registry. |
| `LOG_CONFIG` | no | `/usr/src/app/logging.yaml` | Path to the YAML logging configuration file. Supports `${HOSTNAME}` and other environment-variable substitution (via `string.Template.safe_substitute`). |
| `ACCESS_LOG` | no | `/proc/1/fd/1` | Path for the Gunicorn HTTP access log file. Defaults to stdout. |


## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/version` | Returns application name, version, Python version, and hostname |
| `POST` | `/target` | Registers a service instance as a Prometheus scrape target |
| `GET` | `/targets` | Returns all registered targets in Prometheus HTTP SD format |

### POST /target

Registers a service instance. Called by Master Data Service and Query Service instances on startup and periodically thereafter as a heartbeat to prevent their entries from being marked stale.

**Request body (JSON):**

| Field | Type | Description |
|---|---|---|
| `hostname` | string | Hostname (or `hostname:port`) of the registering instance |
| `service` | string | Service identifier, e.g. `master-data-service` or `query-service` |

Re-posting the same hostname for a service is idempotent — the entry's timestamp is refreshed rather than duplicated.

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
