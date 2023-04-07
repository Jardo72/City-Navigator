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
from json import load


@dataclass(frozen=True, slots=True)
class Config:
    query_service_base_url: str
    test_duration_minutes: int
    journey_plan_search_threads: int
    line_query_threads: int
    station_query_threads: int
    station_filter_threads: int


def read_from_file(filename: str) -> Config:
    with open(filename, "r") as json_file:
        json_data = load(json_file)
        return Config(
            query_service_base_url=json_data["query_service_base_url"],
            test_duration_minutes=json_data["test_duration_minutes"],
            journey_plan_search_threads=json_data["journey_plan_search_threads"],
            line_query_threads=json_data["line_query_threads"],
            station_query_threads=json_data["station_query_threads"],
            station_filter_threads=json_data["station_filter_threads"]
        )
