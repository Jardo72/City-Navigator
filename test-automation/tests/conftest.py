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

import sys
from os import environ
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from rest import MasterDataClient, QueryServiceClient


MASTER_DATA_BASE_URL = environ.get(
    "MASTER_DATA_BASE_URL",
    "http://localhost/city-navigator/api/master-data"
)
QUERY_SERVICE_BASE_URL = environ.get(
    "QUERY_SERVICE_BASE_URL",
    "http://localhost/city-navigator/api/query"
)


@pytest.fixture(scope="session")
def master_data_client():
    return MasterDataClient(MASTER_DATA_BASE_URL)


@pytest.fixture(scope="session")
def query_service_client():
    return QueryServiceClient(QUERY_SERVICE_BASE_URL)
