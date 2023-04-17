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

from typing import Any, Dict, List

import requests

from .dto import ItineraryEntry, Line, LineDetails, MeansOfTransport, Station


def _message_from(response: requests.Response) -> str:
    status_code = response.status_code
    reason = response.reason
    url = response.request.url
    return (
        f"Failed to GET {url} (status code = {status_code}, reason = '{reason}').\n"
        f"Response body:\n{response.text if response.text else ''}"
    )


def _as_line(dict: Dict[str, str]) -> Line:
    return Line(
        uuid=dict["uuid"],
        label=dict["label"],
        means_of_transport=dict["means_of_transport"],
        terminal_stop_one=dict["terminal_stop_one"],
        terminal_stop_two=dict["terminal_stop_two"]
    )


def _as_itinerary(entries: List[Dict[str, Any]]) -> List[ItineraryEntry]:
    result = []
    for current_entry in entries:
        result.append(ItineraryEntry(
            station=_as_station(current_entry["station"]),
            point_in_time_minutes=current_entry["point_in_time_minutes"]
        ))
    return result


def _as_line_details(dict: Dict[str, str]) -> LineDetails:
    return LineDetails(
        uuid=dict["uuid"],
        label=dict["label"],
        means_of_transport=_as_means_of_transport(dict["means_of_transport"]),
        terminal_stop_one=_as_station(dict["terminal_stop_one"]),
        terminal_stop_two=_as_station(dict["terminal_stop_two"]),
        direction_one_itinerary=_as_itinerary(dict["direction_one_itinerary"]),
        direction_two_itinerary=_as_itinerary(dict["direction_two_itinerary"])
    )


def _as_means_of_transport(dict: Dict[str, str]) -> MeansOfTransport:
    return MeansOfTransport(
        uuid=dict["uuid"],
        identifier=dict["identifier"]
    )

def _as_station(dict: Dict[str, str]) -> Station:
    return Station(
        uuid=dict["uuid"],
        name=dict["name"]
    )


class MasterDataClientException(Exception):

    def __init__(self, response: requests.Response) -> None:
        super().__init__(_message_from(response))


class MasterDataClient:

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3,
            pool_block=True
        )
        self._session = requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get_means_of_transport(self) -> List[MeansOfTransport]:
        with self._session:
            response = self._session.get(f"{self._base_url}/means-of-transport")
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_means_of_transport(element) for element in json_array]

    def get_stations(self) -> List[Station]:
        with self._session:
            response = self._session.get(f"{self._base_url}/stations")
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_station(element) for element in json_array]

    def get_station(self, uuid: str) -> Station:
        with self._session:
            response = self._session.get(f"{self._base_url}/station/{uuid}")
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_data = response.json()
            return _as_station(json_data)

    def get_lines(self) -> List[Line]:
        with self._session:
            response = self._session.get(f"{self._base_url}/lines")
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_array = response.json()
            return [_as_line(element) for element in json_array]

    def get_line(self, uuid: str) -> LineDetails:
        with self._session:
            response = requests.get(f"{self._base_url}/line/{uuid}")
            if response.status_code != 200:
                raise MasterDataClientException(response)
            json_data = response.json()
            return _as_line_details(json_data)
