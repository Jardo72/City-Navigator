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
    journey_plan_search_summary: APIEndpointSummary
    station_query_summary: APIEndpointSummary
    station_filter_summary: APIEndpointSummary
    line_query_summary: APIEndpointSummary

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @property
    def start_time(self) -> datetime:
        return min(map(lambda s: s.start_time, self._endpoint_summaries))

    @property
    def end_time(self) -> datetime:
        return max(map(lambda s: s.end_time, self._endpoint_summaries))

    @property
    def overall_success_count(self) -> int:
        return sum(map(lambda s: s.success_count, self._endpoint_summaries))

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
