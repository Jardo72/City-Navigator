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

from __future__ import annotations
from abc import ABC, abstractmethod

from db import SessionLocal

from .client import MasterDataClient


class AbstractSynchronizer(ABC):

    def __init__(self, db: SessionLocal, client: MasterDataClient) -> None:
        self._db = db
        self._client = client

    def __enter__(self) -> AbstractSynchronizer:
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self._db.close()
        self._client.close()

    @property
    def db(self) -> SessionLocal:
        return self._db

    @property
    def client(self) -> MasterDataClient:
        return self._client

    @abstractmethod
    def create_entity(self, uuid: str) -> None:
        ...

    @abstractmethod
    def update_entity(self, uuid: str) -> None:
        ...

    @abstractmethod
    def delete_entity(self, uuid: str) -> None:
        ...
