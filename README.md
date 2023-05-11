# City Navigator

## Introduction
City Navigator is an educational/experimental project for DevOps purposes. It is a simple application based on the microservices architecture, consisting of two microservices exposing REST API - **master data service** and **query service**. The application is a simplifed version of the backend for a portal providing services to passengers using public transport in a city. The master data service allows to manage information about the public transport. It can be used to create, update, delete, and read information about means of transport, stations, and lines (including itineraries). It is meant for some sort of administrators rather than passengers. The query service is meant for passengers, and it allows to serve queries concerning means of transport, stations, and lines (including itineraries). In addition, it can also be used to search journey plans. The underlying data model is very simple, it does not involve any schedules. Besides the above mentioned entities, it also stores information about the edges of the graph representing the city plan. The following diagram outlines the architecture of the application.
![application-diagram](./diagram.png)

The query service is designed so that it should be horizontally scalable and thus capable of dealing with heavy load. Each instance of the service has its own in-memory database, which is initalized upon the start of the instance with data retrieved from the master data service. In order to keep the instances of the query service in sync with the master data, the master data service notifies all instances of the query service via Redis pub/sub whenever there is a change in the master data database (i.e. whenever an entity has been created, updated, or deleted). The journey plan search functionality is based on Dijkstra's shortest-path algorithm.

The application is instrumented with [Prometheus client for Python](https://pypi.org/project/prometheus-client/), so it can publish metrics to Prometheus. Both microservices collect the following metrics:
- number of HTTP (REST) requests for particular API endpoints (Prometheus counter)
- duration of HTTP (REST) requests for particular API endpoints (Prometheus histogram)
- number of failed HTTP (REST) requests for particular API endpoints (Prometheus counter)

In addition, the query service also collects the number of notifications from master data whose processing within the query service has failed (Prometheus counter).


## Tech Stack
Both microservices are implemented in Python using FastAPI and SQLAlchemy. SQLite is used to implement the in-memory database for the query service. For the master data database, more or less any RDBMS supported by SQLAlchemy could be used. The deployments which are part of the project use MariaDB or SQLite (local development with Docker compose). As mentioned before, Redis is used as pub/sub for the notifications sent by the master data service to the query service instance(s). At runtime, [Gunicorn (Green Unicorn)](https://gunicorn.org/) is used as application server. The Dockerfiles which are part of the project configure the server to run in multi-process mode. The above mentioned Prometheus instrumentation is implemented in a way able to deal with the multi-process model properly.


## DevOps
The [dev-ops](./dev-ops) directory is supposed to concentrate various DevOps assets accompanying the application like definition of CI/CD pipelines, IaC configurations etc.

## Test Automation
The [test-automation](./test-automation) directory is supposed to concentrate test automation assets accompanying the application.
