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

from dataclasses import dataclass
from typing import Dict
from uuid import uuid4

from sqlalchemy import create_engine, text

from model import CityPlan, Line


@dataclass(frozen=True, slots=True)
class ImportSummary:
    means_of_transport_count: int
    station_count: int
    line_count: int
    edge_count: int


class _Importer:

    def __init__(self, city_plan: CityPlan, sql_alchemy_db_url: str) -> None:
        self._city_plan = city_plan
        self._means_of_transport: Dict[str, str] = {}
        self._stations: Dict[str, str] = {}
        self._lines: Dict[str, str] = {}
        self._edge_count = 0
        engine = create_engine(
            url=sql_alchemy_db_url,
            echo=False,
            future=True
        )
        self._connection = engine.connect()

    def import_city_plan(self) -> None:
        try:
            for line in self._city_plan.lines:
                self._import_line(line)
            self._connection.commit()
            return ImportSummary(
                means_of_transport_count=len(self._means_of_transport),
                station_count=len(self._stations),
                line_count=len(self._lines),
                edge_count=self._edge_count
            )
        finally:
            self._connection.close()

    def _import_line(self, line: Line) -> None:
        if line.means_of_transport not in self._means_of_transport:
            self._insert_means_of_transport(line.means_of_transport)
        for itinerary_item in line.itinerary:
            if itinerary_item.station not in self._stations:
                self._insert_station(itinerary_item.station)
        self._insert_line(line)
        self._insert_edges(line)

    def _insert_means_of_transport(self, identifier: str) -> None:
        uuid = str(uuid4())
        self._means_of_transport[identifier] = uuid
        self._connection.execute(
            text("insert into T_MEANS_OF_TRANSPORT (UUID, IDENTIFIER) values (:uuid, :identifier)"),
            {"uuid": uuid, "identifier": identifier}
        )

    def _insert_station(self, name: str) -> None:
        uuid = str(uuid4())
        self._stations[name] = uuid
        self._connection.execute(
            text("insert into T_STATIONS (UUID, NAME) values(:uuid, :name)"),
            {"uuid": uuid, "name": name}
        )

    def _insert_line(self, line: Line) -> None:
        uuid = str(uuid4())
        self._lines[line.label] = uuid
        terminal_station_one = line.itinerary[0].station
        terminal_station_two = line.itinerary[-1].station
        self._connection.execute(
            text(
                """
                insert into T_LINES (UUID, LABEL, MEANS_OF_TRANSPORT_UUID, TERMINAL_STOP_ONE_UUID, TERMINAL_STOP_TWO_UUID)
                values (:uuid, :label, :means_of_transport, :terminal_stop_one, :terminal_stop_two)
                """
            ),
            {
                "uuid": uuid,
                "label": line.label,
                "means_of_transport": self._means_of_transport[line.means_of_transport],
                "terminal_stop_one": self._stations[terminal_station_one],
                "terminal_stop_two": self._stations[terminal_station_two]
            }
        )

    def _insert_edges(self, line: Line) -> None:
        station_one = line.itinerary[0].station
        start_point_in_time = line.itinerary[0].point_in_time
        for itinerary_item in line.itinerary[1:]:
            station_two = itinerary_item.station
            distance_min = itinerary_item.point_in_time - start_point_in_time
            print(f"{line.label}: {station_one} <-> {station_two} ({distance_min} min)")
            self._insert_edge(station_one, station_two, line.label, distance_min)
            self._insert_edge(station_two, station_one, line.label, distance_min)
            station_one = station_two
            start_point_in_time = itinerary_item.point_in_time

    def _insert_edge(self, start_station: str, end_station: str, line: str, distance_min: int) -> None:
        uuid = str(uuid4())
        self._connection.execute(
            text(
                """
                insert into T_EDGES (UUID, START_STATION_UUID, END_STATION_UUID, LINE_UUID, DISTANCE_MIN)
                values (:uuid, :start_station, :end_station, :line, :distance)
                """
            ),
            {
                "uuid": uuid,
                "start_station": self._stations[start_station],
                "end_station": self._stations[end_station],
                "line": self._lines[line],
                "distance": distance_min
            }
        )
        self._edge_count += 1


def import_to_database(city_plan: CityPlan, sql_alchemy_db_url: str) -> None:
    importer = _Importer(city_plan, sql_alchemy_db_url)
    return importer.import_city_plan()
