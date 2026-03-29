#
# Copyright 2023 Jaroslav Chmurny
#
# This file is part of City Navigator.
#
# City Navigator is free software developed for educational and experimental
# purposes. It is licensed under the Apache License, Version 2.0 # (the
# "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from foundation.logging_setup import configure_logging
configure_logging()

from contextlib import asynccontextmanager
from logging import getLogger
from socket import gethostname
from sys import version as python_version

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from prometheus_client import CollectorRegistry, Counter
from prometheus_client import make_asgi_app, multiprocess
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config import Config
from foundation.discovery import DiscoveryServiceClient
from rest import router


_logger = getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    _logger.debug("Going to register service instance with Prometheus discovery")
    client = DiscoveryServiceClient(Config.get_prometheus_discovery_base_url(), "master-data-service")
    client.register()
    client.start_heartbeat(Config.get_heartbeat_interval_seconds())

    yield
    ...


APPLICATION_NAME = "City Navigator - Master Data Service"
APPLICATION_VERSION = "0.1.0"


registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)
metrics_app = make_asgi_app(registry=registry)

if Config.is_api_doc_enabled():
    app = FastAPI(title=APPLICATION_NAME, version=APPLICATION_VERSION, root_path=Config.get_root_path(), lifespan=lifespan)
else:
    app = FastAPI(title=APPLICATION_NAME, version=APPLICATION_VERSION, openapi_url=None, redoc_url=None, lifespan=lifespan)
app.include_router(router)
app.mount("/metrics", metrics_app)


http_error_counter = Counter(
    name="master_data_service_http_errors_total",
    documentation="Number of HTTP errors encountered by master data service",
    labelnames=["method", "path", "status_code"]
)


def _is_unique_constraint_violation(exc: IntegrityError) -> bool:
    """Try to recognize unique/duplicate-key constraint violations.

    Different database drivers expose this in different ways; we use
    heuristics to keep this solution generic.
    """
    # PostgreSQL (psycopg2) provides dedicated exception types.
    try:
        import psycopg2

        if isinstance(exc.orig, psycopg2.errors.UniqueViolation):
            return True
    except Exception:
        pass

    # Generic fallback using message text.
    message = str(exc.orig or exc).lower()
    if "unique constraint" in message or "unique violation" in message or "duplicate key" in message:
        return True

    return False


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    route = request.scope.get("route")
    path = route.path if route else request.url.path
    method = request.method
    status_code = exc.status_code
    _logger.error("HTTP exception - path = %s, method = %s, status code = %s", path, method, status_code)
    http_error_counter.labels(method=method, path=path, status_code=status_code).inc()
    return await http_exception_handler(request, exc)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> Response:
    route = request.scope.get("route")
    path = route.path if route else request.url.path
    method = request.method

    if _is_unique_constraint_violation(exc):
        status_code = status.HTTP_409_CONFLICT
        _logger.warning(
            "Unique constraint violation - path = %s, method = %s, detail=%s",
            path,
            method,
            str(exc.orig or exc),
        )
        http_error_counter.labels(method=method, path=path, status_code=status_code).inc()
        return JSONResponse(
            status_code=status_code,
            content={"detail": "Conflict - unique constraint violated"},
        )

    # use exc_info to ensure the full traceback is logged even if FastAPI calls this handler
    # outside of an active exception handling context
    _logger.error("Database exception - path = %s, method = %s", path, method, exc_info=exc)
    http_error_counter.labels(method=method, path=path, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR).inc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> Response:
    route = request.scope.get("route")
    path = route.path if route else request.url.path
    method = request.method
    # use exc_info to ensure the full traceback is logged even if FastAPI calls this handler
    # outside of an active exception handling context
    _logger.error("Database exception - path = %s, method = %s", path, method, exc_info=exc)
    http_error_counter.labels(method=method, path=path, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR).inc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error (database error)"}
    )


class VersionInfo(BaseModel):
    application_name: str
    application_version: str
    python_version: str
    hostname: str


@app.get("/version", response_model=VersionInfo)
async def get_version_info():
    _logger.debug("Asked for version info - app-name = %s, app-version = %s", APPLICATION_NAME, APPLICATION_VERSION)
    return VersionInfo(
        application_name=APPLICATION_NAME,
        application_version=APPLICATION_VERSION,
        python_version=python_version,
        hostname=gethostname()
    )
