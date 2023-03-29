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

from typing import List, Optional
from pydantic import BaseModel


class VersionInfo(BaseModel):
    application_name: str = None
    application_version: str = None
    python_version: str = None


class MeansOfTransportDetails(BaseModel):
    identifier: str = None
    lines: List[str] = None


class LineInfo(BaseModel):
    label: str = None
    means_of_transport: str = None


class StationDetails(BaseModel):
    name: str = None
    lines: List[LineInfo] = None


class JourneyLeg(BaseModel):
    start: str = None
    destination: str = None
    means_of_transport: str = None
    line: str = None
    stop_count: int = None
    duration_minutes: int = None


class JourneyPlan(BaseModel):
    start: str = None
    destination: str = None
    legs: List[JourneyLeg] = None
    stop_count: int = None
    duration_minutes: int = None


class ItineraryEntry(BaseModel):
    station: str = None
    point_in_time_minutes: Optional[int] = None
    transfer: Optional[List[LineInfo]] = None


class LineItinerary(BaseModel):
    start: str = None
    destination: str = None
    entries: List[ItineraryEntry] = None


class LineDetails(BaseModel):
    label: str = None
    means_of_transport: str = None
    direction_one_itinerary: LineItinerary = None
    direction_two_itinerary: LineItinerary = None
