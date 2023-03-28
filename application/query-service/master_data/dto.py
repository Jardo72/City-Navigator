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


@dataclass(frozen=True)
class MeansOfTransport:
    uuid: str
    identifier: str


@dataclass(frozen=True)
class Line:
    uuid: str
    label: str
    means_of_transport_uuid: str
    terminal_stop_one_uuid: str
    terminal_stop_two_uuid: str


@dataclass(frozen=True)
class Station:
    uuid: str
    name: str
