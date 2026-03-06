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

from enum import Enum, unique
from typing import List, Tuple
from uuid import uuid4

from db import Edge, Line, MeansOfTransport, Station

from .dto import LineDetails, LineInfo, LineRequest, ItineraryEntry
from .dto import MeansOfTransportDetails
from .dto import StationDetails


def as_line_info_dto(line: Line) -> LineInfo:
    return LineInfo(
        uuid=line.uuid,
        label=line.label,
        means_of_transport=line.means_of_transport.identifier,
        terminal_stop_one=line.terminal_stop_one.name,
        terminal_stop_two=line.terminal_stop_two.name
    )


def as_station_details_dto(station: Station) -> StationDetails:
    return StationDetails(
        uuid=station.uuid,
        name=station.name
    )


@unique
class _ItineraryDirection(Enum):
    ONE = 1
    TWO = 2


def _as_itinerary_dto(line: Line, direction: _ItineraryDirection) -> List[ItineraryEntry]:
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
        station=as_station_details_dto(current_station),
        point_in_time_minutes=None
    ))
    while current_station is not terminal_stop:
        edge = next(filter(lambda e: e.line is line and e.end_station is not previous_station, current_station.outbound_edges))
        previous_station = current_station
        current_station = edge.end_station
        point_in_time_minutes += edge.distance_min
        entries.append(ItineraryEntry(
            station=as_station_details_dto(current_station),
            point_in_time_minutes=point_in_time_minutes,
        ))
    return entries


def as_line_details_dto(line: Line) -> LineDetails:
    return LineDetails(
        uuid=line.uuid,
        label=line.label,
        means_of_transport=as_means_of_transport_dto(line.means_of_transport),
        terminal_stop_one=as_station_details_dto(line.terminal_stop_one),
        terminal_stop_two=as_station_details_dto(line.terminal_stop_two),
        direction_one_itinerary=_as_itinerary_dto(line, _ItineraryDirection.ONE),
        direction_two_itinerary=_as_itinerary_dto(line, _ItineraryDirection.TWO)
    )


def as_means_of_transport_dto(means_of_transport: MeansOfTransport) -> MeansOfTransportDetails:
    return MeansOfTransportDetails(
        uuid=means_of_transport.uuid,
        identifier=means_of_transport.identifier
    )


def update_line_entity_from_dto(entity: Line, dto: LineRequest) -> None:
    entity.label = dto.label
    entity.means_of_transport_uuid = dto.means_of_transport_uuid
    entity.terminal_stop_one_uuid = dto.terminal_stop_one_uuid
    entity.terminal_stop_two_uuid = dto.terminal_stop_two_uuid


def _itinerary_as_edge_list(dto: LineRequest, line_uuid: str, direction: _ItineraryDirection) -> List[Edge]:
    result = []
    if direction is _ItineraryDirection.ONE:
        itinerary = dto.direction_one_itinerary
    else:
        itinerary = dto.direction_two_itinerary
    for i in range(1, len(itinerary)):
        distance_min = itinerary[i].point_in_time_minutes - itinerary[i - 1].point_in_time_minutes
        result.append(Edge(
            uuid=str(uuid4()),
            distance_min=distance_min,
            start_station_uuid=itinerary[i - 1].station_uuid,
            end_station_uuid=itinerary[i].station_uuid,
            line_uuid=line_uuid
        ))
    return result


def create_edges_from_dto(dto: LineRequest, line_uuid: str) -> Tuple[List[Edge], List[Edge]]:
    itinerary_one = _itinerary_as_edge_list(dto, line_uuid, _ItineraryDirection.ONE)
    itinerary_two = _itinerary_as_edge_list(dto, line_uuid, _ItineraryDirection.TWO)
    return (itinerary_one, itinerary_two)
