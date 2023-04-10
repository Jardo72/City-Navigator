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

from config import Config, read_from_file
from executor import APIEndpointSummary, TestRun, TestRunSummary
from rest import QueryServiceClient
from util import DataCollections


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


def print_api_endpoint_summary(summary: APIEndpointSummary, thread_count: int, test_duration_sec: float) -> None:
    INDENTATION = 4 * " "
    throughput = summary.success_count / test_duration_sec
    print(f"{INDENTATION}Worker thread count:            {thread_count}")
    print(f"{INDENTATION}Number of successful requests:  {summary.success_count}")
    print(f"{INDENTATION}Avg. response time:             {summary.avg_success_duration_millis} millis")
    print(f"{INDENTATION}Min. response time:             {summary.min_success_duration_millis} millis")
    print(f"{INDENTATION}Max. response time:             {summary.max_success_duration_millis} millis")
    print(f"{INDENTATION}Client error count:             {summary.client_error_count}")
    print(f"{INDENTATION}Server error count:             {summary.server_error_count}")
    print(f"{INDENTATION}Throughput:                     {throughput} requests/sec")


def print_test_run_summary(summary: TestRunSummary) -> None:
    FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    duration_sec = summary.duration.total_seconds()
    print(f"Query service base URL: {summary.config.query_service_base_url}")
    print(f"Test run start time:    {summary.start_time.strftime(FORMAT)}")
    print(f"Test run end time:      {summary.end_time.strftime(FORMAT)}")
    print(f"Overall duration:       {summary.duration.total_seconds} secs")
    print("Journey plan search")
    print_api_endpoint_summary(summary.journey_plan_search_summary, summary.config.journey_plan_search_threads, duration_sec)
    print("Station query summary")
    print_api_endpoint_summary(summary.station_query_summary, summary.config.station_query_threads, duration_sec)
    print("Station filter summary")
    print_api_endpoint_summary(summary.station_filter_summary, summary.config.station_filter_threads, duration_sec)
    print("Line query summary")
    print_api_endpoint_summary(summary.line_query_summary, summary.config.line_query_threads, duration_sec)


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    config = read_from_file(command_line_arguments.config_file)
    data_collections = read_lists_from_master_data(config)
    test_run = TestRun(config, data_collections)
    summary = test_run.run()
    print_test_run_summary(summary)


if __name__ == "__main__":
    main()
