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

from typing import List

from config import Config
from util import DataCollections, Summary

from .abstract_test_thread import AbstractTestThread
from .journey_plan_search_thread import JourneyPlanSearchThread
from .line_query_thread import LineQueryThread
from .station_filter_thread import StationFilterThread
from .station_query_thread import StationQueryThread


class TestRun:

    def __init__(self, config: Config, data_collections: DataCollections) -> None:
        self._data_collections = data_collections
        self._config = config
        self._journey_plan_search_threads = [
            JourneyPlanSearchThread(config, data_collections.stations) for _ in range(config.journey_plan_search_threads)
        ]
        self._station_query_threads = [
            StationQueryThread(config, data_collections.stations) for _ in range(config.station_query_threads)
        ]
        self._station_filter_threads = [
            StationFilterThread(config) for _ in range(config.station_filter_threads)
        ]
        self._line_query_threads = [
            LineQueryThread(config, data_collections.lines) for _ in range(config.line_query_threads)
        ]

    def run(self) -> None:
        all_threads = (
            self._journey_plan_search_threads +
            self._station_query_threads +
            self._station_filter_threads +
            self._line_query_threads
        )
        for single_thread in all_threads:
            single_thread.start()

        journey_plan_search_summary = self._wait_for_summary(self._journey_plan_search_threads)
        print()
        print("Journey plan search summary")
        print(journey_plan_search_summary)

        station_query_summary = self._wait_for_summary(self._station_query_threads)
        print()
        print("Station query summary")
        print(station_query_summary)

        station_filter_summary = self._wait_for_summary(self._station_filter_threads)
        print()
        print("Station filter summary")
        print(station_filter_summary)

        line_query_summary = self._wait_for_summary(self._line_query_threads)
        print()
        print("line query summary")
        print(line_query_summary)

    @staticmethod
    def _wait_for_summary(thread_list: List[AbstractTestThread]) -> Summary:
        summary = None
        for thread in thread_list:
            if summary is None:
                summary = thread.wait_for_summary()
            else:
                summary += thread.wait_for_summary()
        return summary
