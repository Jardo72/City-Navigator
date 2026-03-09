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

from abc import ABC
from time import perf_counter
from typing import Any, Dict, Optional

import requests

from .response import Response


class AbstractClient(ABC):

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

    def _parse_json(self, response: requests.Response) -> Optional[Any]:
        if not response.content:
            return None
        try:
            return response.json()
        except Exception:
            return None

    def _get_request(self, path: str, params: Dict[str, str] = None) -> Response:
        start_time = perf_counter()
        response = self._session.get(url=f"{self._base_url}{path}", params=params, timeout=self._TIMEOUT)
        duration_sec = perf_counter() - start_time
        return Response(
            url=response.request.url,
            status_code=response.status_code,
            duration_millis=round(1000 * duration_sec),
            json_data=self._parse_json(response)
        )

    def _post_request(self, path: str, body: Dict) -> Response:
        start_time = perf_counter()
        response = self._session.post(url=f"{self._base_url}{path}", json=body, timeout=self._TIMEOUT)
        duration_sec = perf_counter() - start_time
        return Response(
            url=response.request.url,
            status_code=response.status_code,
            duration_millis=round(1000 * duration_sec),
            json_data=self._parse_json(response)
        )

    def _put_request(self, path: str, body: Dict) -> Response:
        start_time = perf_counter()
        response = self._session.put(url=f"{self._base_url}{path}", json=body, timeout=self._TIMEOUT)
        duration_sec = perf_counter() - start_time
        return Response(
            url=response.request.url,
            status_code=response.status_code,
            duration_millis=round(1000 * duration_sec),
            json_data=self._parse_json(response)
        )

    def _delete_request(self, path: str) -> Response:
        start_time = perf_counter()
        response = self._session.delete(url=f"{self._base_url}{path}", timeout=self._TIMEOUT)
        duration_sec = perf_counter() - start_time
        return Response(
            url=response.request.url,
            status_code=response.status_code,
            duration_millis=round(1000 * duration_sec),
            json_data=self._parse_json(response)
        )
