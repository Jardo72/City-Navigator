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

from db import MeansOfTransport

from .abstract_synchronizer import AbstractSynchronizer


_logger = getLogger("master-data")


class MeansOfTransportSynchronizer(AbstractSynchronizer):

    def create_entity(self, uuid: str) -> None:
        ...

    def update_entity(self, uuid: str) -> None:
        # TODO:
        # client.get_means_of_transport()
        # record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
        # if record:
        #     _logger.debug("Means of transport with uuid %s updated", uuid)
        # else:
        #     _logger.warn("Means of transport with uuid %s not found", uuid)
        ...

    def delete_entity(self, uuid: str) -> None:
        # TODO:
        # record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
        # if record:
        #     db.delete(record)
        #     db.commit()
        #     _logger.debug("Means of transport with uuid %s deleted", uuid)
        # else:
        #     _logger.warn("Means of transport with uuid %s not found", uuid)
        ...

