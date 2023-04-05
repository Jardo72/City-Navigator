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

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from dataclasses import dataclass
from random import randint
from typing import Tuple

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

    def radnom_value(self) -> str:
        random_index = randint(0, self._max_index)
        return self._values[random_index]

    def random_pair(self) -> Tuple[str, str]:
        a = self.radnom_value()
        b = self.radnom_value()
        while a == b:
            b = self.radnom_value()
        return (a, b)


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


def query_journey_plans(config: Config, stations: Tuple[str]) -> None:
    client = QueryServiceClient(config.query_service_base_url)
    selector = RandomSelector(stations)
    for _ in range(100):
        start, destination =selector.random_pair()
        response = client.search_journey_plan(start, destination)
        print(f"Status code = {response.status_code}, duration {response.duration_millis} millis")


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    config = read_from_file(command_line_arguments.config_file)
    data_collections = read_lists_from_master_data(config)
    query_journey_plans(config, data_collections.stations)
    # TODO: 
    # - start the configured number of threads
    # - wait for the completion of threads
    # - summarize the statistics (number of successful/failed requests, min/max/avg response times per request type)
    # - print the statistics


if __name__ == "__main__":
    main()
