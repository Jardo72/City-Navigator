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

from .distance_table import DistanceTable, ShortestPathSearchResult
from .queue import RepriorizablePriorityQueue

from db import Station


def _build_distance_table(start: Station) -> DistanceTable:
    distance_table = DistanceTable(start)
    queue = RepriorizablePriorityQueue()
    explored_stations = {start}

    for edge in start.outbound_edges:
        distance_table.update(edge, edge.distance_min)
        queue.enqueue(
            station=edge.end_station,
            distance_from_start_min=edge.distance_min
        )

    while queue.is_not_empty():
        entry = queue.dequeue()
        current_station = entry.station
        current_distance_from_start_min = entry.distance_from_start_min
        explored_stations.add(current_station)
        for edge in current_station.outbound_edges:
            if edge.end_station in explored_stations:
                continue
            adjacent_distance_from_start = current_distance_from_start_min + edge.distance_min
            if distance_table.update(edge, adjacent_distance_from_start):
                queue.enqueue(
                    station=edge.end_station,
                    distance_from_start_min=adjacent_distance_from_start
                )

    return distance_table


def find_shortest_path(start: Station, destination: Station) -> ShortestPathSearchResult:
    distance_table = _build_distance_table(start)
    return distance_table.backtrack_shortest_path(destination)
