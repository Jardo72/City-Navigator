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

from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.table import Table

from config import Config, read_from_file
from executor import APIEndpointSummary, TestRun, TestRunSummary
from rest import QueryServiceClient
from util import DataCollections


class ReadMasterDataError(Exception):

    def __init__(self, object_type: str, http_status: int) -> None:
        super().__init__(f"Failed to retrieve {object_type} list from master data service (HTTP status = {http_status}).")


def epilog() -> str:
    return """
This tool runs a multi-threaded load test against the City Navigator query service. It sends
concurrent requests to four endpoints (journey plan search, station query, station filter, and
line query), collects response time and error statistics, and prints a summary table. An optional
HTML report can be saved via the -s flag.

Configuration file structure (JSON):
  {
      "query_service_base_url":        "<base URL of the query service>",
      "test_duration_minutes":         <test duration in minutes>,
      "journey_plan_search_threads":   <number of worker threads>,
      "journey_plan_error_percentage": <percentage of intentionally invalid requests>,
      "station_query_threads":         <number of worker threads>,
      "station_query_error_percentage":<percentage of intentionally invalid requests>,
      "station_filter_threads":        <number of worker threads>,
      "line_query_threads":            <number of worker threads>,
      "line_query_error_percentage":   <percentage of intentionally invalid requests>,
      "gradual_load_increase": {
          "worker_start_interval_seconds": <seconds between starting each worker>
      }
  }

Notes:
  - Setting a thread count to 0 disables testing of that endpoint.
  - The error percentage controls how many requests use invalid parameters to verify
    that the service returns the expected 4xx responses.
  - gradual_load_increase is optional. When omitted, all threads start simultaneously.
    When present, workers are shuffled (mixing thread types) and started one by one
    with the configured interval between each. Each thread runs for the full
    test_duration_minutes from its own start, so total wall time is roughly
    (total_threads - 1) * worker_start_interval_seconds plus test_duration_minutes.
"""


def create_command_line_arguments_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="City Navigator - Query Service Load Test",
        formatter_class=RawTextHelpFormatter,
        epilog=epilog(),
    )

    # positional mandatory arguments
    parser.add_argument(
        "config_file",
        help="the name of the JSON file containing the test configuration"
    )

    # optional arguments
    parser.add_argument(
        "-s", "--summary-file",
        dest="summary_file",
        default=None,
        help="the optional name of an HTML file the test run summary is to be written to"
    )

    return parser


def parse_command_line_arguments() -> Namespace:
    parser = create_command_line_arguments_parser()
    params = parser.parse_args()
    return params


def read_lists_from_master_data(config: Config) -> DataCollections:
    client = QueryServiceClient(config.query_service_base_url)

    response = client.get_means_of_transport_list()
    if response.status_code != 200:
        raise ReadMasterDataError("means of transport", response.status_code)
    means_of_transport = map(lambda d: d["identifier"], response.json_data)

    response = client.get_station_list()
    if response.status_code != 200:
        raise ReadMasterDataError("stations", response.status_code)
    stations = map(lambda d: d["name"], response.json_data)

    response = client.get_line_list()
    if response.status_code != 200:
        raise ReadMasterDataError("lines", response.status_code)
    lines = map(lambda d: d["label"], response.json_data)

    return DataCollections(
        means_of_transport=tuple(means_of_transport),
        stations=tuple(stations),
        lines=tuple(lines)
    )


def print_test_run_preview(config: Config, data_collections: DataCollections) -> None:
    print()
    print("Test configuration")
    print(f"Duration:             {config.test_duration_minutes} minutes")
    print(f"Overall thread count: {config.overall_thread_count}")
    if config.gradual_load_increase:
        gli = config.gradual_load_increase
        print(f"Gradual load increase: {gli.worker_start_interval_seconds} sec interval between workers")
    print()
    print("Test data summary")
    print(f"Overall number of stations: {len(data_collections.stations)}")
    print(f"Overall number of lines:    {len(data_collections.lines)}")
    print()


def format_duration(duration_sec: float) -> str:
    duration_sec = round(duration_sec)
    hours, remainder = divmod(duration_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


def _overall_summary_table(summary: TestRunSummary) -> Table:
    FORMAT = "%Y-%m-%d %H:%M:%S"
    duration_sec = summary.duration.total_seconds()
    table = Table(box=box.ROUNDED, show_header=False, title="[cyan]Test Run Summary[/cyan]")
    table.add_column("Parameter", style="bold")
    table.add_column("Value")
    table.add_row("Query service base URL", summary.config.query_service_base_url)
    table.add_row("Start time", summary.start_time.strftime(FORMAT))
    table.add_row("End time", summary.end_time.strftime(FORMAT))
    table.add_row("Duration", format_duration(duration_sec))
    table.add_row("Thread count", str(summary.config.overall_thread_count))
    table.add_row("Overall requests", str(summary.overall_request_count))
    table.add_row("Successful", f"{summary.overall_success_count} ({summary.overall_success_percentage} %)")
    table.add_row("Client errors", f"{summary.overall_client_error_count} ({summary.overall_client_error_percentage} %)")
    table.add_row("Server errors", f"{summary.overall_server_error_count} ({summary.overall_server_error_percentage} %)")
    table.add_row("Exceptions", f"{summary.overall_exception_count} ({summary.overall_exception_percentage} %)")
    return table


def _endpoint_details_table(summary: TestRunSummary) -> Table:
    duration_sec = summary.duration.total_seconds()

    table = Table(box=box.ROUNDED, title="[cyan]Endpoint Details[/cyan]")
    table.add_column("Metric", style="bold")
    table.add_column("Journey Plan Search", justify="right")
    table.add_column("Station Query", justify="right")
    table.add_column("Station Filter", justify="right")
    table.add_column("Line Query", justify="right")

    endpoints = [
        (summary.journey_plan_search_summary, summary.config.journey_plan_search_threads),
        (summary.station_query_summary, summary.config.station_query_threads),
        (summary.station_filter_summary, summary.config.station_filter_threads),
        (summary.line_query_summary, summary.config.line_query_threads),
    ]

    def fmt(s: APIEndpointSummary, t: int, metric: str) -> str:
        if t == 0:
            return "N/A"
        if metric == "threads":
            return str(t)
        if metric == "requests":
            return str(s.overall_request_count)
        if metric == "successful":
            return f"{s.success_count} ({s.success_percentage} %)"
        if metric == "client_errors":
            return f"{s.client_error_count} ({s.client_error_percentage} %)"
        if metric == "server_errors":
            return f"{s.server_error_count} ({s.server_error_percentage} %)"
        if metric == "exceptions":
            return f"{s.exception_count} ({s.exception_percentage} %)"
        if metric == "avg_response":
            return f"{s.avg_success_duration_millis} ms"
        if metric == "min_response":
            return f"{s.min_success_duration_millis} ms"
        if metric == "max_response":
            return f"{s.max_success_duration_millis} ms"
        if metric == "throughput":
            return f"{s.success_count / duration_sec:.1f} req/s"
        return ""

    metrics = [
        ("threads",       "Worker threads"),
        ("requests",      "Requests"),
        ("successful",    "Successful"),
        ("client_errors", "Client errors"),
        ("server_errors", "Server errors"),
        ("exceptions",    "Exceptions"),
        ("avg_response",  "Avg. response time"),
        ("min_response",  "Min. response time"),
        ("max_response",  "Max. response time"),
        ("throughput",    "Throughput"),
    ]

    for key, label in metrics:
        table.add_row(label, *[fmt(s, t, key) for s, t in endpoints])

    return table


def print_test_run_summary(summary: TestRunSummary, console: Console) -> None:
    console.print(Padding(_overall_summary_table(summary), (1, 2)))
    console.print(Padding(_endpoint_details_table(summary), (1, 2)))


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    try:
        config = read_from_file(command_line_arguments.config_file)
        data_collections = read_lists_from_master_data(config)
        print_test_run_preview(config, data_collections)
        test_run = TestRun(config, data_collections)
        summary = test_run.run()
        console = Console(record=bool(command_line_arguments.summary_file))
        print_test_run_summary(summary, console)
        if command_line_arguments.summary_file:
            with open(command_line_arguments.summary_file, mode="w") as f:
                f.write(console.export_html())
    except Exception as e:
        console = Console(record=False)
        console.print()
        console.print("[red]An error occurred during the test run:[/red]")
        console.print(str(e))


if __name__ == "__main__":
    main()
