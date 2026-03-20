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
from time import perf_counter, sleep
from typing import Callable, List, TypeVar

from sqlalchemy.orm import Session

from config import Config

from .client import MasterDataClient
from .dto import LineDetailsMaster, LineMaster, MeansOfTransportMaster, StationMaster
from .mapping import as_means_of_transport, as_station
from .util import import_single_line


_logger = getLogger("master-data")

T = TypeVar("T")


@dataclass(frozen=True)
class RetrievalResult:
    means_of_transport: List[MeansOfTransportMaster]
    stations: List[StationMaster]
    lines: List[LineDetailsMaster]


def _invoke_with_retries(func: Callable[[], T], retries: int = 5, delay_sec: int = 5) -> T:
    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as e:
            _logger.warning(f"Attempt {attempt}/{retries} failed ({func.__name__}): {str(e)}")
            if attempt < retries:
                _logger.info(f"Will retry {func.__name__} after {delay_sec} seconds...")
                sleep(delay_sec)
                delay_sec *= 2  # exponential backoff
            else:
                _logger.error(f"All {retries} attempts failed for {func.__name__}. Giving up.")
                raise e
            

def _retrieve_means_of_transport() -> List[MeansOfTransportMaster]:
    def repeatable_retrieve_means_of_transport() -> List[MeansOfTransportMaster]:
        client = MasterDataClient(Config.get_master_data_service_base_url())
        return client.get_means_of_transport_list()
    return _invoke_with_retries(repeatable_retrieve_means_of_transport)


def _retrieve_stations() -> List[StationMaster]:
    def repeatable_retrieve_stations() -> List[StationMaster]:
        client = MasterDataClient(Config.get_master_data_service_base_url())
        return client.get_station_list()
    return _invoke_with_retries(repeatable_retrieve_stations)


def _retrieve_lines() -> List[LineMaster]:
    def repeatable_retrieve_lines() -> List[LineMaster]:
        client = MasterDataClient(Config.get_master_data_service_base_url())
        return client.get_line_list()
    return _invoke_with_retries(repeatable_retrieve_lines)


def _retrieve_line_details(uuid: str) -> LineDetailsMaster:
    def repeatable_retrieve_line_details() -> LineDetailsMaster:
        client = MasterDataClient(Config.get_master_data_service_base_url())
        return client.get_line(uuid)
    return _invoke_with_retries(repeatable_retrieve_line_details)


def _retrieve_from_master_data_service() -> RetrievalResult:
    TIMEOUT_SEC = 150
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


def _import_lines(db: Session, line_list: List[LineDetailsMaster]) -> None:
    _logger.info("%d lines retrieved from master data", len(line_list))
    for line_details in line_list:
        import_single_line(db, line_details)
    _logger.info("Lines imported into the database")


def init_db_from_master_data(db: Session) -> None:
    start = perf_counter()
    try:
        retrieval_result = _retrieve_from_master_data_service()
        _logger.info("All data retrieved from master data service")
        _import_means_of_transport(db, retrieval_result.means_of_transport)
        _import_stations(db, retrieval_result.stations)
        _import_lines(db, retrieval_result.lines)
        _logger.info("Initialization completed in %.1f seconds", perf_counter() - start)
    except Exception as e:
        _logger.exception("Initialization failed after %.1f seconds", perf_counter() - start)
        raise e
