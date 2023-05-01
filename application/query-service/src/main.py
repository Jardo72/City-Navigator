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

from contextlib import asynccontextmanager
from logging import getLogger
from sys import version as python_version

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from prometheus_client import CollectorRegistry, Counter
from prometheus_client import make_asgi_app, multiprocess
from pydantic import BaseModel

from db import get_db_session
from config import Config
from master_data import init_db_from_master_data
from notifications import subscribe_master_data_notifications
from rest import router


_logger = getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    _logger.info("Going to initialize the in-memory database")
    init_db_from_master_data(get_db_session())

    _logger.info("Going to subscribe Redis notifications")
    subscribe_master_data_notifications()

    yield
    ...


APPLICATION_NAME = "City Navigator - Query Service"
APPLICATION_VERSION = "0.1.0"


registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)
metrics_app = make_asgi_app(registry=registry)

if Config.is_api_doc_enabled():
    app = FastAPI(title=APPLICATION_NAME, root_path=Config.get_root_path(), lifespan=lifespan)
else:
    app = FastAPI(title=APPLICATION_NAME, openapi_url=None, redoc_url=None, lifespan=lifespan)
app.include_router(router)
app.mount("/metrics", metrics_app)


http_error_counter = Counter(
    name="query_service_http_errors_total",
    documentation="Number of HTTP errors encountered by query service",
    labelnames=["method", "path", "status_code"]
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    path = request.url.path
    method = request.method
    status_code = exc.status_code
    _logger.error("HTTP exception - path = %s, method = %s, status code = %s", path, method, status_code)
    http_error_counter.labels(method=method, path=path, status_code=status_code).inc()
    return await http_exception_handler(request, exc)


class VersionInfo(BaseModel):
    application_name: str = None
    application_version: str = None
    python_version: str = None


@app.get("/version", response_model=VersionInfo)
async def get_version_info() -> VersionInfo:
    _logger.debug("Asked for version info - app-name = %s, app-version = %s", APPLICATION_NAME, APPLICATION_VERSION)
    return VersionInfo(
        application_name=APPLICATION_NAME,
        application_version=APPLICATION_VERSION,
        python_version=python_version
    )
