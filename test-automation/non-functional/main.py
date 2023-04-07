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
from threading import Thread
from typing import Tuple

from config import Config, read_from_file
from rest import QueryServiceClient
from util import Collector, RandomSelector, Summary, Timeout


@dataclass(frozen=True, slots=True)
class DataCollections:
    means_of_transport: Tuple[str]
    stations: Tuple[str]
    lines: Tuple[str]


class JourneyPlanSearchThread(Thread):

    def __init__(self, config: Config, stations: Tuple[str]) -> None:
        super().__init__(daemon=False)
        self._summary_collector = Collector()
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

    def get_summary(self) -> Summary:
        return self._summary_collector.get_summary()


class StationQueryThread(Thread):

    def __init__(self, config: Config, stations: Tuple[str]) -> None:
        super().__init__(daemon=False)
        self._summary_collector = Collector()
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

    def get_summary(self) -> Summary:
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

    print()
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
        print(f"Intermediate summary: {summary}")
    print()
    print("Journey plan search summary")
    print(summary)

    print()
    thread_list = []
    for _ in range(config.non_journey_plan_search_threads):
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
        print(f"Intermediate summary: {summary}")
    print()
    print("Station queries summary")
    print(summary)

    # TODO: 
    # - start the configured number of threads
    # - wait for the completion of threads
    # - summarize the statistics (number of successful/failed requests, min/max/avg response times per request type)
    # - print the statistics


if __name__ == "__main__":
    main()
