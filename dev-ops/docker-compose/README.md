# Local Development with Docker Compose
The Docker compose deployment is a simple deployment primarily meant for local development. The deployment is illustrated by the following diagram:
![deployment-diagram](./diagram.png)

This deployment involves a single instance of each of the two microservices comprising the application. In addition, it involves some additional containers:
- Nginx server serving as proxy. All REST requests sent to any of the two microservices are sent to the Nginx server. The server is configured with forwaring rules which direct each request to the proper microservice based on the resource path.
- Redis serving as pub/sub messaging used to deliver notifications from the master data service to all query service instances.
- Prometheus server configured to scrape metrics from both microservices.
- Prometheus HTTP discovery service allowing Prometheus to discover all instances of the microservices, even in deployments with two or more instances of any of the service.
- Grafana configured to use the Prometheus server as a data source.


## SQLite Database for Master-Data Service
TODO
* database file in the [./data](./data) directory
* use the sqlite command line utility to create the database
* use the [](../../application/postgres/init-scripts/create-schema.sql) DDL script to create the database schema
* use the [Data Importer](../../application/data-importer) application to insert the city plan data into the database


## Redis Pub/Sub


## Nginx HTTP Router
TODO:
* configuration in the [./nginx](./nginx) directory


## Prometheus Server
TODO
* configuration in the [./prometheus](./prometheus) directory

## Prometheus HTTP Service Discovery


## Grafana


## HTTP Access Logs for the City Navigator Microservices
TODO
* [access-logs](./access-logs) directory


## Commands
Start the services:
```
docker compose up -d --wait
```

Stop the services:
```
docker compose down
```
