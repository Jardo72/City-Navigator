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


@dataclass(frozen=True, slots=True)
class APIEndpointSummary:
    success_count: int
    client_error_count: int
    server_error_count: int
    overall_success_duration_millis: int
    min_success_duration_millis: int
    max_success_duration_millis: int

    @property
    def avg_success_duration_millis(self) -> int:
        return round(self.overall_success_duration_millis / self.success_count)

    def __add__(self, other: APIEndpointSummary) -> APIEndpointSummary:
        assert isinstance(other, APIEndpointSummary)
        return APIEndpointSummary(
            success_count=self.success_count + other.success_count,
            client_error_count=self.client_error_count + other.client_error_count,
            server_error_count=self.server_error_count + other.server_error_count,
            overall_success_duration_millis=self.overall_success_duration_millis + other.overall_success_duration_millis,
            min_success_duration_millis=min(self.min_success_duration_millis, other.min_success_duration_millis),
            max_success_duration_millis=max(self.max_success_duration_millis, other.max_success_duration_millis)
        )
