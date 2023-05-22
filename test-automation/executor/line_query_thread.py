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

from typing import Tuple

from config import Config
from rest import QueryServiceClient, Response
from util import RandomSelector

from .abstract_test_thread import AbstractTestThread


class LineQueryThread(AbstractTestThread):

    def __init__(self, config: Config, lines: Tuple[str]) -> None:
        super().__init__(config)
        self._lines = RandomSelector(lines)

    def send_single_request(self, client: QueryServiceClient) -> Response:
        label = self._lines.random_value()
        return client.get_line_details(label)
