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
from db import Edge, Line, MeansOfTransport, Station

from .client import MasterDataClient
from .dto import LineDetails


_logger = getLogger('master-data-import')


def _import_means_of_transport(db: Session, client: MasterDataClient) -> None:
    means_of_transport_list = client.get_means_of_transport()
    _logger.info("%d means of transport retrieved from master data", len(means_of_transport_list))
    for means_of_transport in means_of_transport_list:
        db.add(MeansOfTransport(
            uuid=means_of_transport.uuid,
            identifier=means_of_transport.identifier
        ))
    db.commit()
    _logger.info("Means of transport imported from master data service")


def _import_stations(db: Session, client: MasterDataClient) -> None:
    station_list = client.get_stations()
    _logger.info("%d stations retrieved from master data", len(station_list))
    for station in station_list:
        db.add(Station(
            uuid=station.uuid,
            name=station.name
        ))
    db.commit()
    _logger.info("Stations imported from master data service")


def _import_single_line(db: Session, line_details: LineDetails) -> None:
    line = Line()
    line.uuid = line_details.uuid
    line.label = line_details.label
    line.means_of_transport_uuid = line_details.means_of_transport.uuid
    line.terminal_stop_one_uuid = line_details.terminal_stop_one.uuid
    line.terminal_stop_two_uuid = line_details.terminal_stop_two.uuid
    db.add(line)
    db.commit()


def _import_lines(db: Session, client: MasterDataClient) -> None:
    line_list = client.get_lines()
    _logger.info("%d lines retrieved from master data", len(line_list))
    for line_dto in line_list:
        line_details = client.get_line(line_dto.uuid)
        _import_single_line(db, line_details)


def init_db_from_master_data(db: Session) -> None:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    # TODO:
    # - retrieval of data from the master data service could be parallelized
    # - we could simply collect all the data from the master service
    # - the DB inserts can be done sequentially when all the data has been
    #   retrieved
    _import_means_of_transport(db, client)
    _import_stations(db, client)
    _import_lines(db, client)
