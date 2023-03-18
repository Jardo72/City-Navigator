from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Any, Dict, Tuple

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
    """Immutable structure carrying a single element currently being present
    in the priority queue.
    This class is just an internal helper structure, it it not part of the
    public API of the :class: RepriorizablePriorityQueue class.
    """
    priority: int
    item: Any = field(compare=False)
    irrelevant: bool = False


class _RepriorizablePriorityQueue:

    def __init__(self) -> None:
        self._heap = []
        self._size = 0
        self._sequence = 0
        self._item_map: Dict[Any, _QueueEntry] = {}


    def is_not_empty(self) -> bool:
        return self._size > 0
