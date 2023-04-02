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

from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Dict, List

from db import Station


@dataclass(order=True, slots=True)
class QueueEntry:
    station: Station = field(compare=False)
    distance_from_start_min: int
    irrelevant: bool = False


class RepriorizablePriorityQueue:

    def __init__(self) -> None:
        self._heap: List[QueueEntry] = []
        self._size = 0
        self._station_map: Dict[Station, QueueEntry] = {}


    def is_not_empty(self) -> bool:
        return self._size > 0


    def enqueue(self, station: Station, distance_from_start_min: int) -> None:
        queue_entry = QueueEntry(station, distance_from_start_min)
        heappush(self._heap, queue_entry)
        if station in self._station_map:
            self._station_map[station].irrelevant = True
        else:
            self._size += 1
        self._station_map[station] = queue_entry

    def dequeue(self) -> QueueEntry:
        while len(self._heap) > 0:
            queue_entry = heappop(self._heap)
            if queue_entry.irrelevant:
                continue
            self._station_map.pop(queue_entry.station)
            self._size -= 1
            return queue_entry
        message = 'Cannot dequeue from empty queue.'
        raise IndexError(message)
