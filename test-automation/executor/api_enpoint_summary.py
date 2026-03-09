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

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class APIEndpointSummary:
    start_time: datetime
    end_time: datetime
    success_count: int
    client_error_count: int
    server_error_count: int
    exception_count: int
    overall_success_duration_millis: int
    min_success_duration_millis: int
    max_success_duration_millis: int

    @property
    def overall_request_count(self) -> int:
        return self.success_count + self.client_error_count + self.server_error_count + self.exception_count

    @property
    def success_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.success_count / self.overall_request_count), 1)

    @property
    def client_error_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.client_error_count / self.overall_request_count), 1)

    @property
    def server_error_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.server_error_count / self.overall_request_count), 1)

    @property
    def exception_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.exception_count / self.overall_request_count), 1)

    @property
    def avg_success_duration_millis(self) -> int:
        if self.success_count == 0:
            return 0
        return round(self.overall_success_duration_millis / self.success_count)

    def __add__(self, other: APIEndpointSummary) -> APIEndpointSummary:
        assert isinstance(other, APIEndpointSummary)
        return APIEndpointSummary(
            start_time=min(self.start_time, other.start_time),
            end_time=max(self.end_time, other.end_time),
            success_count=self.success_count + other.success_count,
            client_error_count=self.client_error_count + other.client_error_count,
            server_error_count=self.server_error_count + other.server_error_count,
            exception_count=self.exception_count + other.exception_count,
            overall_success_duration_millis=self.overall_success_duration_millis + other.overall_success_duration_millis,
            min_success_duration_millis=min(self.min_success_duration_millis, other.min_success_duration_millis),
            max_success_duration_millis=max(self.max_success_duration_millis, other.max_success_duration_millis)
        )
