# City Navigator - Query Service

## Introduction

## Configuration
The service is configured via environment variables. This design is driven by the fact that the service is supposed to be deployed in Docker containers. The following list describes each of the environment variables relevant for the configuration:
* MASTER_DATA_SERVICE_BASE_URL
* DATABASE_URL

## Prometheus Metrics
* HTTP request count (count)
* HTTP error count (count)
* HTTP request duration (histogram)
