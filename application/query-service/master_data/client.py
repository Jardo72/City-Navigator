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

from typing import Dict, List

import requests

from .dto import Line, MeansOfTransport, Station


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
        means_of_transport_uuid=dict["means_of_transport"]["uuid"],
        terminal_stop_one_uuid=dict["terminal_stop_one"]["uuid"],
        terminal_stop_two_uuid=dict["terminal_stop_two"]["uuid"]
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

    def get_means_of_transport(self) -> List[MeansOfTransport]:
        response = requests.get(f"{self._base_url}/means-of-transport")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        json_array = response.json()
        return [_as_means_of_transport(element) for element in json_array]

    def get_stations(self) -> List[Station]:
        response = requests.get(f"{self._base_url}/stations")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        json_array = response.json()
        return [_as_station(element) for element in json_array]

    def get_lines(self) -> List[Line]:
        response = requests.get(f"{self._base_url}/lines")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        json_array = response.json()
        return [_as_line(element) for element in json_array]
