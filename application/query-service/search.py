from collections import deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Dict, List, Tuple

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


@dataclass(order=True, slots=True)
class _QueueEntry:
    station: Station = field(compare=False)
    distance_from_start_min: int
    irrelevant: bool = False


class _RepriorizablePriorityQueue:

    def __init__(self) -> None:
        self._heap: List[_QueueEntry] = []
        self._size = 0
        self._station_map: Dict[Station, _QueueEntry] = {}


    def is_not_empty(self) -> bool:
        return self._size > 0


    def enqueue(self, station: Station, distance_from_start_min: int) -> None:
        queue_entry = _QueueEntry(station, distance_from_start_min)
        heappush(self._heap, queue_entry)
        if station in self._station_map:
            self._station_map[station].irrelevant = True
        else:
            self._size += 1
        self._station_map[station] = queue_entry

    def dequeue(self) -> _QueueEntry:
        while len(self._heap) > 0:
            queue_entry = heappop(self._heap)
            if queue_entry.irrelevant:
                continue
            self._station_map.pop(queue_entry.station)
            self._size -= 1
            return queue_entry.item
        message = 'Cannot dequeue from empty queue.'
        raise IndexError(message)


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


class _DistanceTable:
    
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


def _build_distance_table(start: Station) -> _DistanceTable:
    distance_table = _DistanceTable(start)
    queue = _RepriorizablePriorityQueue()
    explored_stations = {start}

    for edge in start.outbound_edges:
        distance_table.update(edge, edge.distance_min)
        queue.enqueue(_QueueEntry(
            station=edge.end_station,
            distance_from_start_min=edge.distance_min
        ))

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
                queue.enqueue(_QueueEntry(
                    station=edge.end_station,
                    distance_from_start_min=adjacent_distance_from_start
                ))

    return distance_table


def find_shortest_path(start: Station, destination: Station) -> ShortestPathSearchResult:
    distance_table = _build_distance_table(start)
    return distance_table.backtrack_shortest_path(destination)
