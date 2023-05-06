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

from typing import List
from uuid import uuid4

from sqlalchemy.orm import Session

from db import Edge, Line

from .dto import ItineraryEntryMaster, LineDetailsMaster


def _import_itinerary(db: Session, line_uuid: str, entries: List[ItineraryEntryMaster]) -> None:
    previous_station_uuid = entries[0].station.uuid
    previous_point_in_time_minutes = 0
    for current_entry in entries[1:]:
        distance_minutes = current_entry.point_in_time_minutes - previous_point_in_time_minutes
        current_station_uuid = current_entry.station.uuid
        db.add(Edge(
            uuid=str(uuid4()),
            distance_min=distance_minutes,
            start_station_uuid=previous_station_uuid,
            end_station_uuid=current_station_uuid,
            line_uuid=line_uuid
        ))
        previous_point_in_time_minutes = current_entry.point_in_time_minutes
        previous_station_uuid = current_entry.station.uuid


def import_single_line(db: Session, line_details: LineDetailsMaster) -> None:
    line = Line()
    line.uuid = line_details.uuid
    line.label = line_details.label
    line.means_of_transport_uuid = line_details.means_of_transport.uuid
    line.terminal_stop_one_uuid = line_details.terminal_stop_one.uuid
    line.terminal_stop_two_uuid = line_details.terminal_stop_two.uuid
    db.add(line)
    _import_itinerary(db, line_details.uuid, line_details.direction_one_itinerary)
    _import_itinerary(db, line_details.uuid, line_details.direction_two_itinerary)
    db.commit()

