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

from json import dumps
from logging import getLogger
from socket import gethostname

import requests


_logger = getLogger("discovery")


class DiscoveryServiceClient:

    def __init__(self, base_url: str) -> None:
        self._session = requests.Session()
        self._base_url = base_url

    def register(self) -> None:
        # TODO: hardcoded port
        request = {
            "hostname": f"{gethostname()}:8000",
            "service": "master-data-service"
        }
        with self._session:
            response = self._session.post(f"{self._base_url}/target", data=dumps(request))
            _logger.debug("Registration - status code = %s", response.status_code)
