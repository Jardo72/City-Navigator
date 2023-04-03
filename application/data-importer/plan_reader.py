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

from json import load
from typing import Any, Dict, List, Tuple

from model import Line, LineItineraryItem, CityPlan


def _read_single_itinerary(json_data: Dict[str, Any]) -> Tuple[LineItineraryItem, ...]:
    result = []
    for element in json_data:
        station = element['station']
        point_in_time = element['pointInTime']
        result.append(LineItineraryItem(station, point_in_time))
    return tuple(result)


def _read_single_line(json_data: Dict[str, Any]) -> Line:
    label = json_data['label']
    means_of_transport = json_data['meansOfTransport']
    itinerary = _read_single_itinerary(json_data['itinerary'])
    return Line(label, means_of_transport, itinerary)


def _read_from_dict(json_data: Dict[str, Any]) -> CityPlan:
    lines: List[Line] = []
    version = json_data['version']
    for element in json_data['lines']:
        line = _read_single_line(element)
        lines.append(line)
    return CityPlan(version, tuple(lines))


def read_from_file(filename: str) -> CityPlan:
    with open(filename, "r") as json_file:
        json_string = load(json_file)
        return _read_from_dict(json_string)
