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

from db_importer import ImportSummary
from db_importer import import_to_database
from plan_reader import read_from_file


def create_command_line_arguments_parser() -> ArgumentParser:
    parser = ArgumentParser(description="City Navigator - Data Importer", formatter_class=RawTextHelpFormatter)

    # positional mandatory arguments
    parser.add_argument(
        "input_file",
        help="the name of the input JSON file containing the city plan"
    )

    return parser


def parse_command_line_arguments() -> Namespace:
    parser = create_command_line_arguments_parser()
    params = parser.parse_args()
    return params


def print_summary(import_summary: ImportSummary) -> None:
    print(f"Number of imported means of transport: {import_summary.means_of_transport_count}")
    print(f"Number of imported stations:           {import_summary.station_count}")
    print(f"Number of imported lines:              {import_summary.line_count}")
    print(f"Number of imported edges:              {import_summary.edge_count}")


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    city_plan = read_from_file(command_line_arguments.input_file)
    import_summary = import_to_database(city_plan)
    print_summary(import_summary)


if __name__ == "__main__":
    main()
