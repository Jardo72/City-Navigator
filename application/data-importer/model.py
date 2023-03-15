from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True, slots=True)
class LineItineraryItem:
    station: str
    point_in_time: int


@dataclass(frozen=True, slots=True)
class Line:
    label: str
    means_of_transport: str
    itinerary: Tuple[LineItineraryItem, ...]


@dataclass(frozen=True, slots=True)
class CityPlan:
    version: str
    lines: Tuple[Line, ...]
