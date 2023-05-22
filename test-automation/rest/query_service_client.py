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

from .abstract_client import AbstractClient
from .response import Response


class QueryServiceClient(AbstractClient):

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def get_means_of_transport_list(self) -> Response:
        return self._get_request("/means-of-transport")

    def get_station_list(self, filter: str = None) -> Response:
        if filter is None:
            return self._get_request("/stations")
        return self._get_request("/stations", params={"filter": filter})

    def get_station_details(self, name: str) -> Response:
        return self._get_request("/station", params={"name": name})

    def get_line_list(self) -> Response:
        return self._get_request("/lines")

    def get_line_details(self, label: str) -> Response:
        return self._get_request("/line", params={"label": label})

    def search_journey_plan(self, start: str, destination: str) -> Response:
        return self._get_request("/journey-plan", params={"start": start, "destination": destination})
