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

from collections import deque
from dataclasses import dataclass
from typing import Dict, Tuple

from db import Edge, Station


@dataclass(frozen=True, slots=True)
class ShortestPathSearchResult:
    path: Tuple[Edge, ...]

    @property
    def start(self) -> Station:
        return self.path[0].start_station

    @property
    def destination(self) -> Station:
        return self.path[-1].end_station

    @property
    def overall_distance_min(self) -> int:
        return sum(map(lambda edge: edge.distance_min, self.path))


@dataclass(slots=True)
class _DistanceTableEntry:
    edge_from_previous_station: Edge
    distance_from_start_min: int

    def update(self, edge: Edge, distance_from_start_min) -> bool:
        if self.distance_from_start_min > distance_from_start_min:
            self.distance_from_start_min = distance_from_start_min
            self.edge_from_previous_station = edge
            return True
        return False


class DistanceTable:
    
    def __init__(self, start_station: Station) -> None:
        self._start_station = start_station
        self._entries: Dict[Station, _DistanceTableEntry] = {}

    def update(self, edge: Edge, distance_from_start_min: int) -> bool:
        if edge.end_station in self._entries:
            return self._entries[edge.end_station].update(edge, distance_from_start_min)
        self._entries[edge.end_station] = _DistanceTableEntry(edge, distance_from_start_min)
        return True

    def backtrack_shortest_path(self, destination: Station) -> ShortestPathSearchResult:
        if destination not in self._entries:
            message = f'There is no path from {self._start_station.name} to {destination.name}.'
            raise ValueError(message)
        path = deque()
        edge_from_previous_station = self._entries[destination].edge_from_previous_station
        path.appendleft(edge_from_previous_station)
        while edge_from_previous_station.start_station is not self._start_station:
            previous_station = edge_from_previous_station.start_station
            edge_from_previous_station = self._entries[previous_station].edge_from_previous_station
            path.appendleft(edge_from_previous_station)
        return ShortestPathSearchResult(path=tuple(path))
