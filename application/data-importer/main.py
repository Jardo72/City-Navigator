from dataclasses import dataclass
from json import load
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True, slots=True)
class LineItineraryItem:
    station: str
    point_in_time: int


@dataclass(frozen=True)
class Line:
    identifier: str
    means_of_transport: str
    itinerary: Tuple[LineItineraryItem, ...]


@dataclass(frozen=True)
class ModelDefinition:
    version: str
    lines: Tuple[Line, ...]


def _read_single_itinerary(json_data: Dict[str, Any]) -> Tuple[LineItineraryItem, ...]:
    result = []
    for element in json_data:
        station = element['station']
        point_in_time = element['pointInTime']
        result.append(LineItineraryItem(station, point_in_time))
    return tuple(result)


def _read_single_line(json_data: Dict[str, Any]) -> Line:
    identifier = json_data['identifier']
    means_of_transport = json_data['meansOfTransport']
    itinerary = _read_single_itinerary(json_data['itinerary'])
    return Line(identifier, means_of_transport, itinerary)


def _read_from_dict(json_data: Dict[str, Any]) -> ModelDefinition:
    lines: List[Line] = []
    version = json_data['version']
    for element in json_data['lines']:
        line = _read_single_line(element)
        lines.append(line)
    return ModelDefinition(version, tuple(lines))


def _read_from_file(filename: str) -> ModelDefinition:
    with open(filename, "r") as json_file:
        json_string = load(json_file)
        return _read_from_dict(json_string)


def main() -> None:
    city_plan = _read_from_file("city-plan.json")
    print(city_plan)


if __name__ == "__main__":
    main()
