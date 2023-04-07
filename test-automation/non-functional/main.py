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

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from dataclasses import dataclass
from random import randint
from threading import Thread
from time import perf_counter
from typing import Tuple

from abstract_client import Response
from config import Config, read_from_file
from query_service_client import QueryServiceClient


@dataclass(frozen=True, slots=True)
class DataCollections:
    means_of_transport: Tuple[str]
    stations: Tuple[str]
    lines: Tuple[str]


class RandomSelector:

    def __init__(self, values: Tuple[str]) -> None:
        self._values = values
        self._max_index = len(values) - 1

    def random_value(self) -> str:
        random_index = randint(0, self._max_index)
        return self._values[random_index]

    def random_pair(self) -> Tuple[str, str]:
        a = self.random_value()
        b = self.random_value()
        while a == b:
            b = self.random_value()
        return (a, b)


class Timeout:

    def __init__(self, timeout_min: int) -> None:
        self._start_time = perf_counter()
        self._timeout_millis = 60 * 1000 * timeout_min

    def has_not_expired_yet(self) -> bool:
        current_time = perf_counter()
        return (1000 * (current_time - self._start_time)) < self._timeout_millis


@dataclass(frozen=True, slots=True)
class TestThreadSummary:
    success_count: int
    client_error_count: int
    server_error_count: int
    overall_success_duration_millis: int
    min_success_duration_millis: int
    max_success_duration_millis: int

    @property
    def avg_success_duration_millis(self) -> int:
        return round(self.overall_success_duration_millis / self.success_count)

    def __add__(self, other: TestThreadSummary) -> TestThreadSummary:
        assert isinstance(other, TestThreadSummary)
        return TestThreadSummary(
            success_count=self.success_count + other.success_count,
            client_error_count=self.client_error_count + other.client_error_count,
            server_error_count=self.server_error_count + other.server_error_count,
            overall_success_duration_millis=self.overall_success_duration_millis + other.overall_success_duration_millis,
            min_success_duration_millis=self.min_success_duration_millis + other.min_success_duration_millis,
            max_success_duration_millis=self.max_success_duration_millis + other.max_success_duration_millis
        )


class TestThreadSummaryCollector:

    def __init__(self) -> None:
        self._success_count: int = 0
        self._client_error_count: int = 0
        self._server_error_count: int = 0
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

    def get_summary(self) -> TestThreadSummary:
        return TestThreadSummary(
            success_count=self._success_count,
            client_error_count=self._client_error_count,
            server_error_count=self._server_error_count,
            overall_success_duration_millis=self._overall_success_duration_millis,
            min_success_duration_millis=self._min_success_duration_millis,
            max_success_duration_millis=self._max_success_duration_millis
        )


class JourneyPlanSearchThread(Thread):

    def __init__(self, config: Config, stations: Tuple[str]) -> None:
        super().__init__(daemon=False)
        self._summary_collector = TestThreadSummaryCollector()
        self._stations = stations
        self._config = config

    def run(self) -> None:
        client = QueryServiceClient(self._config.query_service_base_url)
        timeout = Timeout(self._config.test_duration_minutes)
        selector = RandomSelector(self._stations)
        while timeout.has_not_expired_yet():
            for _ in range(10):
                start, destination = selector.random_pair()
                response = client.search_journey_plan(start, destination)
                self._summary_collector.add(response)

    def get_summary(self) -> TestThreadSummary:
        return self._summary_collector.get_summary()


class StationQueryThread(Thread):

    def __init__(self, config: Config, stations: Tuple[str]) -> None:
        super().__init__(daemon=False)
        self._summary_collector = TestThreadSummaryCollector()
        self._stations = stations
        self._config = config

    def run(self) -> None:
        client = QueryServiceClient(self._config.query_service_base_url)
        timeout = Timeout(self._config.test_duration_minutes)
        selector = RandomSelector(self._stations)
        while timeout.has_not_expired_yet():
            for _ in range(10):
                name = selector.random_value()
                response = client.get_station_details(name)
                self._summary_collector.add(response)

    def get_summary(self) -> TestThreadSummary:
        return self._summary_collector.get_summary()


def create_command_line_arguments_parser() -> ArgumentParser:
    parser = ArgumentParser(description="City Navigator - Query Service Load Test", formatter_class=RawTextHelpFormatter)

    # positional mandatory arguments
    parser.add_argument(
        "config_file",
        help="the name of the JSON file containing the test configuration"
    )

    return parser


def parse_command_line_arguments() -> Namespace:
    parser = create_command_line_arguments_parser()
    params = parser.parse_args()
    return params


def read_lists_from_master_data(config: Config) -> DataCollections:
    client = QueryServiceClient(config.query_service_base_url)

    response = client.get_means_of_transport_list()
    assert response.status_code == 200
    means_of_transport = map(lambda d: d["identifier"], response.json_data)

    response = client.get_station_list()
    assert response.status_code == 200
    stations = map(lambda d: d["name"], response.json_data)

    response = client.get_line_list()
    assert response.status_code == 200
    lines = map(lambda d: d["label"], response.json_data)

    return DataCollections(
        means_of_transport=tuple(means_of_transport),
        stations=tuple(stations),
        lines=tuple(lines)
    )


def query_lines(config: Config, lines: Tuple[str]) -> None:
    client = QueryServiceClient(config.query_service_base_url)
    timeout = Timeout(config.test_duration_minutes)
    selector = RandomSelector(lines)
    while timeout.has_not_expired_yet():
        for _ in range(10):
            label = selector.random_value()
            response = client.get_line_details(label)
            print(f"Status code = {response.status_code}, duration {response.duration_millis} millis")


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    config = read_from_file(command_line_arguments.config_file)
    data_collections = read_lists_from_master_data(config)
    thread_list = []
    for _ in range(config.journey_plan_search_threads):
        thread = JourneyPlanSearchThread(config, data_collections.stations)
        thread_list.append(thread)
        thread.start()
    summary = None
    for thread in thread_list:
        thread.join()
        if summary is None:
            summary = thread.get_summary()
        else:
            summary += thread.get_summary()
    print()
    print("Journey plan search summary")
    print(summary)

    thread_list = []
    for _ in range(config.journey_plan_search_threads):
        thread = StationQueryThread(config, data_collections.stations)
        thread_list.append(thread)
        thread.start()
    summary = None
    for thread in thread_list:
        thread.join()
        if summary is None:
            summary = thread.get_summary()
        else:
            summary += thread.get_summary()
    print()
    print("Stations queries summary")
    print(summary)

    # TODO: 
    # - start the configured number of threads
    # - wait for the completion of threads
    # - summarize the statistics (number of successful/failed requests, min/max/avg response times per request type)
    # - print the statistics


if __name__ == "__main__":
    main()
