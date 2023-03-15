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
    identifier = json_data['identifier']
    means_of_transport = json_data['meansOfTransport']
    itinerary = _read_single_itinerary(json_data['itinerary'])
    return Line(identifier, means_of_transport, itinerary)


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
