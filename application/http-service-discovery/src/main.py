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

from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from socket import gethostname
from sys import version as python_version
from threading import Lock
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel


_logger = getLogger("main")


APPLICATION_NAME = "City Navigator - Prometheus HTTP Service Discovery"
APPLICATION_VERSION = "0.1.0"


app = FastAPI(title=APPLICATION_NAME, version=APPLICATION_VERSION, openapi_url=None, redoc_url=None)


class VersionInfo(BaseModel):
    application_name: str = None
    application_version: str = None
    python_version: str = None
    hostname: str


class TargetListEntry(BaseModel):
    targets: List[str]
    labels: Dict[str, str]


class TargetInfo(BaseModel):
    hostname: str
    service: str


@dataclass(frozen=True, slots=True)
class TargetRegistryEntry:
    hostname: str
    timestamp: datetime


class TargetRegistry:

    def __init__(self) -> None:
        self._lock = Lock()
        self._entries = {}

    def add(self, hostname: str, service: str) -> None:
        with self._lock:
            _logger.debug("Hostname %s added to or updated in the registry (service = %s)", hostname, service)
            if service not in self._entries:
                self._entries[service] = set()
            entry = TargetRegistryEntry(hostname=hostname, timestamp=datetime.now())
            self._entries[service].add(entry)

    def get_targets_grouped_by_service(self) -> Dict[str, str]:
        with self._lock:
            result = {}
            for service, entries in self._entries.items():
                hostnames = list(map(lambda host: host.hostname, entries))
                distinct_hostnames = set(hostnames)
                result[service] = list(distinct_hostnames)
            return result


target_registry = TargetRegistry()


@app.get("/version", response_model=VersionInfo)
async def get_version_info():
    _logger.debug("Asked for version info - app-name = %s, app-version = %s", APPLICATION_NAME, APPLICATION_VERSION)
    return VersionInfo(
        application_name=APPLICATION_NAME,
        application_version=APPLICATION_VERSION,
        python_version=python_version,
        hostname=gethostname()
    )


@app.post("/target")
async def register_target(request: TargetInfo):
    _logger.debug("Asked to register target %s", request.hostname)
    target_registry.add(request.hostname, request.service)


@app.get("/targets", response_model=List[TargetListEntry])
async def get_targets():
    _logger.debug("Asked for targets")
    targets = target_registry.get_targets_grouped_by_service()
    result = []
    for service, hostnames in targets.items():
        result.append(TargetListEntry(
            targets=list(hostnames),
            labels={"service": service}
        ))
    return result
