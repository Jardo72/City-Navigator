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
from typing import Any, Dict, List

import requests

from .dto import ItineraryEntryMaster, LineMaster, LineDetailsMaster, MeansOfTransportMaster, StationMaster


_logger = getLogger("master-data")


def _message_from(response: requests.Response) -> str:
    status_code = response.status_code
    reason = response.reason
    url = response.request.url
    return (
        f"Failed to GET {url} (status code = {status_code}, reason = '{reason}').\n"
        f"Response body:\n{response.text if response.text else ''}"
    )


def _as_line(dict: Dict[str, str]) -> LineMaster:
    return LineMaster(
        uuid=dict["uuid"],
        label=dict["label"],
        means_of_transport=dict["means_of_transport"],
        terminal_stop_one=dict["terminal_stop_one"],
        terminal_stop_two=dict["terminal_stop_two"]
    )


def _as_itinerary(entries: List[Dict[str, Any]]) -> List[ItineraryEntryMaster]:
    result = []
    for current_entry in entries:
        result.append(ItineraryEntryMaster(
            station=_as_station(current_entry["station"]),
            point_in_time_minutes=current_entry["point_in_time_minutes"]
        ))
    return result


def _as_line_details(dict: Dict[str, str]) -> LineDetailsMaster:
    return LineDetailsMaster(
        uuid=dict["uuid"],
        label=dict["label"],
        means_of_transport=_as_means_of_transport(dict["means_of_transport"]),
        terminal_stop_one=_as_station(dict["terminal_stop_one"]),
        terminal_stop_two=_as_station(dict["terminal_stop_two"]),
        direction_one_itinerary=_as_itinerary(dict["direction_one_itinerary"]),
        direction_two_itinerary=_as_itinerary(dict["direction_two_itinerary"])
    )


def _as_means_of_transport(dict: Dict[str, str]) -> MeansOfTransportMaster:
    return MeansOfTransportMaster(
        uuid=dict["uuid"],
        identifier=dict["identifier"]
    )

def _as_station(dict: Dict[str, str]) -> StationMaster:
    return StationMaster(
        uuid=dict["uuid"],
        name=dict["name"]
    )


class MasterDataClientException(Exception):

    def __init__(self, response: requests.Response) -> None:
        super().__init__(_message_from(response))


class MasterDataClient:

    _TIMEOUT = (15, 15)

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self._session = requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get_means_of_transport_list(self) -> List[MeansOfTransportMaster]:
        _logger.debug("Going to retrieve list of means of transport from master data service")
        with self._session:
            response = self._session.get(f"{self._base_url}/means-of-transport", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_means_of_transport(element) for element in json_array]

    def get_means_of_transport(self, uuid: str) -> MeansOfTransportMaster:
        _logger.debug("Going to retrieve means of transport (uuid = %s) from master data service", uuid)
        with self._session:
            response = self._session.get(f"{self._base_url}/means-of-transport/{uuid}", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_data = response.json()
            return _as_means_of_transport(json_data)

    def get_station_list(self) -> List[StationMaster]:
        _logger.debug("Going to retrieve list of stations from master data service")
        with self._session:
            response = self._session.get(f"{self._base_url}/stations", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_station(element) for element in json_array]

    def get_station(self, uuid: str) -> StationMaster:
        _logger.debug("Going to retrieve station (uuid = %s) from master data service", uuid)
        with self._session:
            response = self._session.get(f"{self._base_url}/station/{uuid}", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_data = response.json()
            return _as_station(json_data)

    def get_line_list(self) -> List[LineMaster]:
        _logger.debug("Going to retrieve list of lines from master data service")
        with self._session:
            response = self._session.get(f"{self._base_url}/lines", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_line(element) for element in json_array]

    def get_line(self, uuid: str) -> LineDetailsMaster:
        _logger.debug("Going to retrieve line (uuid = %s) from master data service", uuid)
        with self._session:
            response = requests.get(f"{self._base_url}/line/{uuid}", timeout=self._TIMEOUT)
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_data = response.json()
            return _as_line_details(json_data)

    def close(self) -> None:
        self._session.close()
