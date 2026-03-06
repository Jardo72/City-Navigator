#
# Copyright 2026 Jaroslav Chmurny
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


class MasterDataClient(AbstractClient):

    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)

    def get_means_of_transport_list(self) -> Response:
        return self._get_request("/means-of-transport")

    def get_means_of_transport(self, uuid: str) -> Response:
        return self._get_request(f"/means-of-transport/{uuid}")

    def create_means_of_transport(self, identifier: str, presentation_color: str = None) -> Response:
        body = {"identifier": identifier}
        if presentation_color is not None:
            body["presentation_color"] = presentation_color
        return self._post_request("/means-of-transport", body)

    def update_means_of_transport(self, uuid: str, identifier: str, presentation_color: str = None) -> Response:
        body = {"identifier": identifier}
        if presentation_color is not None:
            body["presentation_color"] = presentation_color
        return self._put_request(f"/means-of-transport/{uuid}", body)

    def delete_means_of_transport(self, uuid: str) -> Response:
        return self._delete_request(f"/means-of-transport/{uuid}")

    def get_station_list(self) -> Response:
        return self._get_request("/stations")

    def get_station(self, uuid: str) -> Response:
        return self._get_request(f"/station/{uuid}")

    def create_station(self, name: str) -> Response:
        return self._post_request("/station", {"name": name})

    def update_station(self, uuid: str, name: str) -> Response:
        return self._put_request(f"/station/{uuid}", {"name": name})

    def delete_station(self, uuid: str) -> Response:
        return self._delete_request(f"/station/{uuid}")

    def get_line_list(self) -> Response:
        return self._get_request("/lines")

    def get_line(self, uuid: str) -> Response:
        return self._get_request(f"/line/{uuid}")

    def create_line(self, label: str, means_of_transport_uuid: str,
                    terminal_stop_one_uuid: str, terminal_stop_two_uuid: str,
                    direction_one_itinerary: list, direction_two_itinerary: list) -> Response:
        return self._post_request("/line", {
            "label": label,
            "means_of_transport_uuid": means_of_transport_uuid,
            "terminal_stop_one_uuid": terminal_stop_one_uuid,
            "terminal_stop_two_uuid": terminal_stop_two_uuid,
            "direction_one_itinerary": direction_one_itinerary,
            "direction_two_itinerary": direction_two_itinerary,
        })

    def delete_line(self, uuid: str) -> Response:
        return self._delete_request(f"/line/{uuid}")
