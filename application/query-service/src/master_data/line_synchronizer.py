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

from logging import getLogger

from db import Line, SessionLocal

from .abstract_synchronizer import AbstractSynchronizer
from .client import MasterDataClient


_logger = getLogger("master-data")


class LineSynchronizer(AbstractSynchronizer):

    def __init__(self, db: SessionLocal, client: MasterDataClient) -> None:
        super().__init__(db, client)

    def create_entity(self, uuid: str) -> None:
        ...

    def update_entity(self, uuid: str) -> None:
        record = self.db.query(Line).filter(Line.uuid == uuid).first()
        if record:
            # TODO: update and commit the record
            line_dto = self.client.get_line(uuid)
            _logger.debug("Line with uuid %s updated", uuid)
        else:
            _logger.warn("Line with uuid %s not found", uuid)

    def delete_entity(self, uuid: str) -> None:
        record = self.db.query(Line).filter(Line.uuid == uuid).first()
        if record:
            self.db.delete(record)
            self.db.commit()
            _logger.debug("Line with uuid %s deleted", uuid)
        else:
            _logger.warn("Line with uuid %s not found", uuid)
