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

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

from db import get_db_session
from master_data import init_db_from_master_data
from rest import router


_logger = getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    _logger.info("Going to initialize the in-memory database")
    init_db_from_master_data(get_db_session())

    yield
    ...


APPLICATION_NAME = "City Navigator - Query Service"
APPLICATION_VERSION = "0.1.0"


app = FastAPI(title=APPLICATION_NAME, lifespan=lifespan)
app.include_router(router)
Instrumentator().instrument(app).expose(app)


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
