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

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from config import Config
from db import Edge, Line

from .client import MasterDataClient
from .dto import ItineraryEntryMaster, LineDetailsMaster, LineMaster, MeansOfTransportMaster, StationMaster
from .mapping import as_means_of_transport, as_station


_logger = getLogger("master-data")


@dataclass(frozen=True)
class RetrievalResult:
    means_of_transport: List[MeansOfTransportMaster]
    stations: List[StationMaster]
    lines: List[LineDetailsMaster]


def _retrieve_means_of_transport() -> List[MeansOfTransportMaster]:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    return client.get_means_of_transport_list()


def _retrieve_stations() -> List[StationMaster]:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    return client.get_station_list()


def _retrieve_lines() -> List[LineMaster]:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    return client.get_line_list()


def _retrieve_line_details(uuid: str) -> LineDetailsMaster:
    client = MasterDataClient(Config.get_master_data_service_base_url())
    return client.get_line(uuid)


def _retrieve_from_master_data_service() -> RetrievalResult:
    TIMEOUT_SEC = 15
    with ThreadPoolExecutor(max_workers=6) as executor:
        lines_future = executor.submit(_retrieve_lines)
        means_of_transport_future = executor.submit(_retrieve_means_of_transport)
        stations_future = executor.submit(_retrieve_stations)
        line_details_future_list = []
        for line in lines_future.result(timeout=TIMEOUT_SEC):
            line_details_future = executor.submit(_retrieve_line_details, line.uuid)
            line_details_future_list.append(line_details_future)
        return RetrievalResult(
            means_of_transport=means_of_transport_future.result(timeout=TIMEOUT_SEC),
            stations=stations_future.result(timeout=TIMEOUT_SEC),
            lines=[f.result(timeout=TIMEOUT_SEC) for f in line_details_future_list]
        )


def _import_means_of_transport(db: Session, means_of_transport_list: List[MeansOfTransportMaster]) -> None:
    _logger.info("%d means of transport retrieved from master data", len(means_of_transport_list))
    for means_of_transport_master in means_of_transport_list:
        db.add(as_means_of_transport(means_of_transport_master))
    db.commit()
    _logger.info("Means of transport imported into the database")


def _import_stations(db: Session, station_list: List[StationMaster]) -> None:
    _logger.info("%d stations retrieved from master data", len(station_list))
    for station_master in station_list:
        db.add(as_station(station_master))
    db.commit()
    _logger.info("Stations imported into the database")


def _import_itinerary(db: Session, line_uuid: str, entries: List[ItineraryEntryMaster]) -> None:
    previous_station_uuid = entries[0].station.uuid
    previous_point_in_time_minutes = 0
    for current_entry in entries[1:]:
        distance_minutes = current_entry.point_in_time_minutes - previous_point_in_time_minutes
        current_station_uuid = current_entry.station.uuid
        db.add(Edge(
            uuid=str(uuid4()),
            distance_min=distance_minutes,
            start_station_uuid=previous_station_uuid,
            end_station_uuid=current_station_uuid,
            line_uuid=line_uuid
        ))
        previous_point_in_time_minutes = current_entry.point_in_time_minutes
        previous_station_uuid = current_entry.station.uuid


def _import_single_line(db: Session, line_details: LineDetailsMaster) -> None:
    line = Line()
    line.uuid = line_details.uuid
    line.label = line_details.label
    line.means_of_transport_uuid = line_details.means_of_transport.uuid
    line.terminal_stop_one_uuid = line_details.terminal_stop_one.uuid
    line.terminal_stop_two_uuid = line_details.terminal_stop_two.uuid
    db.add(line)
    _import_itinerary(db, line_details.uuid, line_details.direction_one_itinerary)
    _import_itinerary(db, line_details.uuid, line_details.direction_two_itinerary)
    db.commit()


def _import_lines(db: Session, line_list: List[LineDetailsMaster]) -> None:
    _logger.info("%d lines retrieved from master data", len(line_list))
    for line_details in line_list:
        _import_single_line(db, line_details)
    _logger.info("Lines imported into the database")


def init_db_from_master_data(db: Session) -> None:
    retrieval_result = _retrieve_from_master_data_service()
    _logger.info("All data retrieved from master data service")
    _import_means_of_transport(db, retrieval_result.means_of_transport)
    _import_stations(db, retrieval_result.stations)
    _import_lines(db, retrieval_result.lines)
