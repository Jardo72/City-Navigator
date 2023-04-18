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

from logging import getLogger
from typing import List

from pydantic import BaseModel, Field, root_validator


_logger = getLogger("rest")


class MeansOfTransportDetails(BaseModel):
    uuid: str = None
    identifier: str = None
    presentation_color: str = None


class MeansOfTransportRequest(BaseModel):
    identifier: str = None
    presentation_color: str = None


class StationDetails(BaseModel):
    uuid: str = None
    name: str = None


class StationRequest(BaseModel):
    name: str = None


class LineInfo(BaseModel):
    uuid: str = None
    label: str = None
    means_of_transport: str = None
    terminal_stop_one: str = None
    terminal_stop_two: str = None


class ItineraryEntry(BaseModel):
    station: StationDetails = None
    point_in_time_minutes: int = None


class LineDetails(BaseModel):
    uuid: str = None
    label: str = None
    means_of_transport: MeansOfTransportDetails = None
    terminal_stop_one: StationDetails = None
    terminal_stop_two: StationDetails = None
    direction_one_itinerary: List[ItineraryEntry] = None
    direction_two_itinerary: List[ItineraryEntry] = None


class ItineraryEntryRequest(BaseModel):
    station_uuid: str = None
    point_in_time_minutes: int = None


class LineRequest(BaseModel):
    label: str = None
    means_of_transport_uuid: str = None
    terminal_stop_one_uuid: str = None
    terminal_stop_two_uuid: str = None
    direction_one_itinerary: List[ItineraryEntryRequest] = None
    direction_two_itinerary: List[ItineraryEntryRequest] = None

    @root_validator
    def line_request_validator(cls, values):
        _logger.debug("Starting the validation of LineRequest, values = %s", values)
        terminal_stop_one = values.get("terminal_stop_one_uuid")
        terminal_stop_two = values.get("terminal_stop_two_uuid")
        direction_one_itinerary = values.get("direction_one_itinerary")
        direction_two_itinerary = values.get("direction_two_itinerary")

        if terminal_stop_one != direction_one_itinerary[0].station_uuid:
            message = "Terminal stop 1 does not match with the starting station of itinerary 1."
            raise ValueError(message)
        if terminal_stop_two != direction_one_itinerary[-1].station_uuid:
            message = "Terminal stop 2 does not match with the end station of itinerary 1."
            raise ValueError(message)
        if terminal_stop_one != direction_two_itinerary[-1].station_uuid:
            message = "Terminal stop 1 does not match with the end station of itinerary 2."
            raise ValueError(message)
        if terminal_stop_two != direction_two_itinerary[0].station_uuid:
            message = "Terminal stop 2 does not match with the starting station of itinerary 2."
            raise ValueError(message)
        return values
