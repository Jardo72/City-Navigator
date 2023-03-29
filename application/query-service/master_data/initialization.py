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

from sqlalchemy.orm import Session

from config import Config
from db import MeansOfTransport, Station

from .client import MasterDataClient


_logger = getLogger('master-data-import')


def init_db_from_master_data(db: Session) -> None:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    means_of_transport_list = client.get_means_of_transport()
    _logger.info("%d means of transport retrieved from master data", len(means_of_transport_list))
    for means_of_transport in means_of_transport_list:
        db.add(MeansOfTransport(
            uuid=means_of_transport.uuid,
            identifier=means_of_transport.identifier
        ))

    station_list = client.get_stations()
    _logger.info("%d stations retrieved from master data", len(station_list))
    for station in station_list:
        db.add(Station(
            uuid=station.uuid,
            name=station.name
        ))
    db.commit()

    line_list = client.get_lines()
    _logger.info("%d lines retrieved from master data", len(line_list))
    for line in line_list:
        ...
