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

from random import shuffle
from time import sleep
from typing import List


from rich.progress import track


from config import Config
from util import DataCollections, Timeout

from .abstract_test_thread import AbstractTestThread
from .api_enpoint_summary import APIEndpointSummary
from .journey_plan_search_thread import JourneyPlanSearchThread
from .line_query_thread import LineQueryThread
from .station_filter_thread import StationFilterThread
from .station_query_thread import StationQueryThread
from .test_run_summary import TestRunSummary


class TestRun:

    def __init__(self, config: Config, data_collections: DataCollections) -> None:
        self._data_collections = data_collections
        self._config = config
        self._timeout = Timeout(config.test_duration_minutes)
        self._journey_plan_search_threads = [
            JourneyPlanSearchThread(
                config,
                self._timeout,
                data_collections.stations,
                config.journey_plan_error_percentage
            ) for _ in range(config.journey_plan_search_threads)
        ]
        self._station_query_threads = [
            StationQueryThread(
                config,
                self._timeout,
                data_collections.stations,
                config.station_query_error_percentage
            ) for _ in range(config.station_query_threads)
        ]
        self._station_filter_threads = [
            StationFilterThread(
                config,
                self._timeout,
            ) for _ in range(config.station_filter_threads)
        ]
        self._line_query_threads = [
            LineQueryThread(
                config,
                self._timeout,
                data_collections.lines,
                config.line_query_error_percentage
            ) for _ in range(config.line_query_threads)
        ]

    def run(self) -> TestRunSummary:
        all_threads = (
            self._journey_plan_search_threads +
            self._station_query_threads +
            self._station_filter_threads +
            self._line_query_threads
        )

        if self._config.gradual_load_increase:
            self._start_threads_gradually(all_threads)
        else:
            for single_thread in all_threads:
                single_thread.start()

        self._timeout.start()
        self._display_progress()

        for single_thread in all_threads:
            single_thread.join()

        journey_plan_search_summary = self._calculate_summary(self._journey_plan_search_threads)
        station_query_summary = self._calculate_summary(self._station_query_threads)
        station_filter_summary = self._calculate_summary(self._station_filter_threads)
        line_query_summary = self._calculate_summary(self._line_query_threads)

        return TestRunSummary(
            config=self._config,
            journey_plan_search_summary=journey_plan_search_summary,
            station_query_summary=station_query_summary,
            station_filter_summary=station_filter_summary,
            line_query_summary=line_query_summary,
        )

    def _start_threads_gradually(self, all_threads: List[AbstractTestThread]) -> None:
        interval = self._config.gradual_load_increase.worker_start_interval_seconds
        threads = all_threads.copy()
        shuffle(threads)
        total = len(threads)
        print(f"Gradual load increase: starting {total} worker(s) with {interval} sec interval between each")
        for i, thread in enumerate(threads):
            thread.start()
            print(f"  Started {type(thread).__name__} ({i + 1}/{total})")
            if i < total - 1:
                sleep(interval)

    def _display_progress(self) -> None:
        print()
        overall_duration_seconds = self._config.test_duration_minutes * 60
        if overall_duration_seconds > 600:
            sleep_duration_seconds = overall_duration_seconds / 100
            steps = 100
        else:
            sleep_duration_seconds = overall_duration_seconds / 20
            steps = 20
        for _ in track(range(steps)):
            sleep(sleep_duration_seconds)

    @staticmethod
    def _calculate_summary(thread_list: List[AbstractTestThread]) -> APIEndpointSummary:
        summary = None
        for thread in thread_list:
            if summary is None:
                summary = thread.get_summary()
            else:
                summary += thread.get_summary()
        return summary
