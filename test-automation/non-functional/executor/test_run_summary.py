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

from dataclasses import dataclass
from datetime import datetime

from config import Config

from .api_enpoint_summary import APIEndpointSummary


@dataclass(frozen=True, slots=True)
class TestRunSummary:
    config: Config
    start_time: datetime
    end_time: datetime
    journey_plan_search_summary: APIEndpointSummary
    station_query_summary: APIEndpointSummary
    station_filter_summary: APIEndpointSummary
    line_query_summary: APIEndpointSummary
