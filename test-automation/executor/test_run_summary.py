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

from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import List

from config import Config

from .api_enpoint_summary import APIEndpointSummary


@dataclass(frozen=True, slots=True)
class TestRunSummary:
    config: Config
    main_phase_start_time: datetime
    journey_plan_search_summary: APIEndpointSummary
    station_query_summary: APIEndpointSummary
    station_filter_summary: APIEndpointSummary
    line_query_summary: APIEndpointSummary

    @property
    def ramp_up_start_time(self) -> datetime:
        return min(map(lambda s: s.start_time, self._endpoint_summaries))

    @property
    def total_duration(self) -> timedelta:
        return self.end_time - self.ramp_up_start_time

    @property
    def main_phase_duration(self) -> timedelta:
        return self.end_time - self.main_phase_start_time

    @property
    def end_time(self) -> datetime:
        return max(map(lambda s: s.end_time, self._endpoint_summaries))

    @property
    def overall_request_count(self) -> int:
        return sum(map(lambda s: s.overall_request_count, self._endpoint_summaries))

    @property
    def overall_success_count(self) -> int:
        return sum(map(lambda s: s.success_count, self._endpoint_summaries))

    @property
    def overall_success_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.overall_success_count / self.overall_request_count), 1)

    @property
    def overall_client_error_count(self) -> int:
        return sum(map(lambda s: s.client_error_count, self._endpoint_summaries))

    @property
    def overall_client_error_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.overall_client_error_count / self.overall_request_count), 1)

    @property
    def overall_server_error_count(self) -> int:
        return sum(map(lambda s: s.server_error_count, self._endpoint_summaries))

    @property
    def overall_server_error_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.overall_server_error_count / self.overall_request_count), 1)

    @property
    def overall_exception_count(self) -> int:
        return sum(map(lambda s: s.exception_count, self._endpoint_summaries))

    @property
    def overall_exception_percentage(self) -> float:
        if self.overall_request_count == 0:
            return 0.0
        return round(100 * (self.overall_exception_count / self.overall_request_count), 1)

    @property
    def _endpoint_summaries(self) -> List[APIEndpointSummary]:
        result = []
        for field in fields(self):
            if field.type is not APIEndpointSummary:
                continue
            summary = getattr(self, field.name)
            if summary:
                result.append(summary)
        return result
