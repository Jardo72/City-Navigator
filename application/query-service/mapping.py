from enum import Enum, unique
from typing import List

from db import Line, MeansOfTransport, Station
from dto import ItineraryEntry, LineDetails, LineInfo, LineItinerary
from dto import MeansOfTransportDetails, StationDetails


def as_means_of_transport_details(means_of_transport: MeansOfTransport) -> MeansOfTransportDetails:
    line_names=[line.label for line in means_of_transport.lines]
    line_names.sort()
    return MeansOfTransportDetails(
        identifier=means_of_transport.identifier,
        lines=line_names
    )


def as_line_info(line: Line) -> LineInfo:
    return LineInfo(
        label=line.label,
        means_of_transport=line.means_of_transport.identifier
    )


@unique
class _ItineraryDirection(Enum):
    ONE = 1
    TWO = 2


def _lines_except_of(station: Station, excluded_line: Line) -> List[LineInfo]:
    unique_lines = set()
    result = []
    for edge in station.outbound_edges:
        if edge.line is excluded_line or edge.line in unique_lines:
            continue
        unique_lines.add(edge.line)
        result.append(as_line_info(edge.line))
    return result


def _as_itinerary(line: Line, direction: _ItineraryDirection) -> LineItinerary:
    entries = []
    if direction is _ItineraryDirection.ONE:
        current_station = line.terminal_stop_one
        terminal_stop = line.terminal_stop_two
    else:
        current_station = line.terminal_stop_two
        terminal_stop = line.terminal_stop_one
    previous_station = None
    point_in_time_minutes = 0
    entries.append(ItineraryEntry(
        station=current_station.name,
        point_in_time_minutes=None,
        transfer=_lines_except_of(station=current_station, excluded_line=line)
    ))
    while current_station is not terminal_stop:
        edge = next(filter(lambda e: e.line is line and e.end_station is not previous_station, current_station.outbound_edges))
        previous_station = current_station
        current_station = edge.end_station
        point_in_time_minutes += edge.distance_min
        entries.append(ItineraryEntry(
            station=current_station.name,
            point_in_time_minutes=point_in_time_minutes,
            transfer=_lines_except_of(station=current_station, excluded_line=line)
        ))
    if direction is _ItineraryDirection.ONE:
        return LineItinerary(
            start=line.terminal_stop_one.name,
            destination=line.terminal_stop_two.name,
            entries=entries
        )
    else:
        return LineItinerary(
            start=line.terminal_stop_two.name,
            destination=line.terminal_stop_one.name,
            entries=entries
        )


def as_line_details(line: Line) -> LineDetails:
    return LineDetails(
        label=line.label,
        means_of_transport=line.means_of_transport.identifier,
        direction_one_itinerary=_as_itinerary(line, _ItineraryDirection.ONE),
        direction_two_itinerary=_as_itinerary(line, _ItineraryDirection.TWO)
    )


def as_station_details(station: Station) -> StationDetails:
    unique_lines = set()
    lines = []
    for single_edge in station.outbound_edges:
        if single_edge.line.label not in unique_lines:
            unique_lines.add(single_edge.line.label)
            lines.append(LineInfo(
                label=single_edge.line.label,
                means_of_transport=single_edge.line.means_of_transport.identifier
            ))
    return StationDetails(
        name=station.name,
        lines=lines
    )
