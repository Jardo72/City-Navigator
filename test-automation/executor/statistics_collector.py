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

from datetime import datetime

from rest import Response

from .api_enpoint_summary import APIEndpointSummary

class StatisticsCollector:

    def __init__(self) -> None:
        self._success_count: int = 0
        self._client_error_count: int = 0
        self._server_error_count: int = 0
        self._exception_count = 0
        self._overall_success_duration_millis: int = 0
        self._min_success_duration_millis: int = 1000000
        self._max_success_duration_millis: int = 0

    def add(self, response: Response) -> None:
        if 200 <= response.status_code < 300:
            self._success_count += 1
            self._overall_success_duration_millis += response.duration_millis
            if self._min_success_duration_millis > response.duration_millis:
                self._min_success_duration_millis = response.duration_millis
            if self._max_success_duration_millis < response.duration_millis:
                self._max_success_duration_millis = response.duration_millis
        if 400 <= response.status_code < 500:
            self._client_error_count += 1
        if 500 <= response.status_code < 600:
            self._server_error_count += 1

    def test_thread_started(self) -> None:
        self._start_time = datetime.now()

    def test_thread_completed(self) -> None:
        self._end_time = datetime.now()

    def exception_caught(self) -> None:
        self._exception_count += 1

    def get_summary(self) -> APIEndpointSummary:
        return APIEndpointSummary(
            start_time=self._start_time,
            end_time=self._end_time,
            success_count=self._success_count,
            client_error_count=self._client_error_count,
            server_error_count=self._server_error_count,
            exception_count=self._exception_count,
            overall_success_duration_millis=self._overall_success_duration_millis,
            min_success_duration_millis=self._min_success_duration_millis,
            max_success_duration_millis=self._max_success_duration_millis
        )
