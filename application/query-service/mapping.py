from enum import Enum, unique

from db import Line, Station
from dto import ItineraryEntry, LineDetails, LineInfo, LineItinerary
from dto import MeansOfTransportDetails, StationDetails


@unique
class ItineraryDirection(Enum):
    ONE = 1
    TWO = 2


def as_line_info(line: Line) -> LineInfo:
    return LineInfo(
        label=line.label,
        means_of_transport=line.means_of_transport.identifier
    )


def as_itinerary(line: Line, direction: ItineraryDirection) -> LineItinerary:
    entries = []
    if direction is ItineraryDirection.ONE:
        current_station = line.terminal_stop_one
        terminal_stop = line.terminal_stop_two
    else:
        current_station = line.terminal_stop_two
        terminal_stop = line.terminal_stop_one
    previous_station = None
    point_in_time_minutes = 0
    entries.append(ItineraryEntry(
        station=current_station.name,
        point_in_time_minutes=None
    ))
    while current_station is not terminal_stop:
        edge = next(filter(lambda e: e.line is line and e.end_station is not previous_station, current_station.outbound_edges))
        previous_station = current_station
        current_station = edge.end_station
        point_in_time_minutes += edge.distance_min
        entries.append(ItineraryEntry(
            station=current_station.name,
            point_in_time_minutes=point_in_time_minutes
        ))
    if direction is ItineraryDirection.ONE:
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
        direction_one_itinerary=as_itinerary(line, ItineraryDirection.ONE),
        direction_two_itinerary=as_itinerary(line, ItineraryDirection.TWO)
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
