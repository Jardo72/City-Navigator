from enum import Enum, unique
from typing import List, Optional

from db import Edge, Line, MeansOfTransport, Station
from dto import ItineraryEntry, LineDetails, LineInfo, LineItinerary
from dto import MeansOfTransportDetails, StationDetails
from dto import JourneyLeg, JourneyPlan
from search import ShortestPathSearchResult


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


class _JourneyPlanBuilder:

    def __init__(self) -> None:
        self._legs: List[JourneyLeg] = []
        self._current_leg: List[Edge] = []
        self._current_line: Optional[Line] = None

    def _summarize_current_leg(self) -> JourneyLeg:
        return JourneyLeg(
            start=self._current_leg[0].start_station.name,
            destination=self._current_leg[-1].end_station.name,
            means_of_transport= self._current_line.means_of_transport.identifier,
            line=self._current_line.label,
            stop_count=len(self._current_leg),
            duration_minutes=sum(map(lambda edge: edge.distance_min, self._current_leg))
        )

    def add_edge(self, edge: Edge) -> None:
        if self._current_line is None:
            self._current_leg.append(edge)
            self._current_line = edge.line
            return
        
        if self._current_line == edge.line:
            self._current_leg.append(edge)
            return

        self._legs.append(self._summarize_current_leg())
        self._current_leg = [edge]
        self._current_line = edge.line

    def build(self) -> JourneyPlan:
        self._legs.append(self._summarize_current_leg())
        return JourneyPlan(
            start=self._legs[0].start,
            destination=self._legs[-1].destination,
            legs=self._legs,
            stop_count=sum(map(lambda leg: leg.stop_count, self._legs)),
            duration_minutes=sum(map(lambda leg: leg.duration_minutes, self._legs))
        )


def as_journey_plan(search_result: ShortestPathSearchResult) -> JourneyPlan:
    builder = _JourneyPlanBuilder()
    for edge in search_result.path:
        builder.add_edge(edge)
    return builder.build()