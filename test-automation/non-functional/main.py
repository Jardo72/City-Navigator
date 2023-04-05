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

from config import read_from_file


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


def main() -> None:
    command_line_arguments = parse_command_line_arguments()
    config = read_from_file(command_line_arguments.config_file)
    print(config)
    # TODO: 
    # - load the lists of means of transport, lines & stations so you can use them to generate random requests
    # - start the configured number of threads
    # - wait for the completion of threads
    # - summarize the statistics (number of successful/failed requests, min/max/avg response times per request type)


if __name__ == "__main__":
    main()
