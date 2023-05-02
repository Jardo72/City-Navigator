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

from abc import ABC, abstractmethod
from threading import Thread

from config import Config
from rest import QueryServiceClient, Response
from util import Timeout

from .api_enpoint_summary import APIEndpointSummary
from .statistics_collector import StatisticsCollector


class AbstractTestThread(Thread, ABC):

    def __init__(self, config: Config) -> None:
        super().__init__(daemon=False)
        self._summary_collector = StatisticsCollector()
        self._config = config

    def run(self) -> None:
        client = QueryServiceClient(self._config.query_service_base_url)
        timeout = Timeout(self._config.test_duration_minutes)
        self._summary_collector.test_thread_started()
        while timeout.has_not_expired_yet():
            for _ in range(5):
                try:
                    response = self.send_single_request(client)
                    self._summary_collector.add(response)
                except Exception as e:
                    self._summary_collector.exception_caught()
        self._summary_collector.test_thread_completed()

    @abstractmethod
    def send_single_request(self, client: QueryServiceClient) -> Response:
        ...

    def get_summary(self) -> APIEndpointSummary:
        return self._summary_collector.get_summary()
