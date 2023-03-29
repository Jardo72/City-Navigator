from enum import Enum, unique
from typing import List

from db import Line, MeansOfTransport, Station
from dto import LineDetails, LineInfo, ItineraryEntry
from dto import MeansOfTransportDetails
from dto import StationDetails


def as_line_info(line: Line) -> LineInfo:
    return LineInfo(
        uuid=line.uuid,
        label=line.label,
        means_of_transport=line.means_of_transport.identifier,
        terminal_stop_one=line.terminal_stop_one.name,
        terminal_stop_two=line.terminal_stop_two.name
    )


def as_station_details(station: Station) -> StationDetails:
    return StationDetails(
        uuid=station.uuid,
        name=station.name
    )


@unique
class _ItineraryDirection(Enum):
    ONE = 1
    TWO = 2


def _as_itinerary(line: Line, direction: _ItineraryDirection) -> List[ItineraryEntry]:
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
        station=as_station_details(current_station),
        point_in_time_minutes=None
    ))
    while current_station is not terminal_stop:
        edge = next(filter(lambda e: e.line is line and e.end_station is not previous_station, current_station.outbound_edges))
        previous_station = current_station
        current_station = edge.end_station
        point_in_time_minutes += edge.distance_min
        entries.append(ItineraryEntry(
            station=as_station_details(current_station),
            point_in_time_minutes=point_in_time_minutes,
        ))
    return entries


def as_line_details(line: Line) -> LineDetails:
    return LineDetails(
        uuid=line.uuid,
        label=line.label,
        means_of_transport=as_means_of_transport(line.means_of_transport),
        terminal_stop_one=as_station_details(line.terminal_stop_one),
        terminal_stop_two=as_station_details(line.terminal_stop_two),
        direction_one_itinerary=_as_itinerary(line, _ItineraryDirection.ONE),
        direction_two_itinerary=_as_itinerary(line, _ItineraryDirection.TWO)
    )


def as_means_of_transport(means_of_transport: MeansOfTransport) -> MeansOfTransportDetails:
    return MeansOfTransportDetails(
        uuid=means_of_transport.uuid,
        identifier=means_of_transport.identifier
    )
