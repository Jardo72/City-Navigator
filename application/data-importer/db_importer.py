from typing import Dict
from uuid import uuid4

from sqlalchemy import create_engine, text

from model import CityPlan, Line


class _Importer:

    def __init__(self, city_plan: CityPlan) -> None:
        self._city_plan = city_plan
        self._means_of_transport: Dict[str, str] = {}
        self._stations: Dict[str, str] = {}
        engine = create_engine(
            url="sqlite:///./test.db",
            echo=True,
            future=True,
            connect_args={"check_same_thread": False}
        )
        self._connection = engine.connect()

    def import_city_plan(self) -> None:
        try:
            for line in self._city_plan.lines:
                self._import_line(line)
            self._connection.commit()
        finally:
            self._connection.close()

    def _import_line(self, line: Line) -> None:
        if line.means_of_transport not in self._means_of_transport:
            self._import_means_of_transport(line.means_of_transport)
        for itinerary_item in line.itinerary:
            if itinerary_item.station not in self._stations:
                self._import_station(itinerary_item.station)

    def _import_station(self, name: str) -> None:
        uuid = str(uuid4())
        self._stations[name] = uuid
        print(f"{uuid} -> {name}")
        self._connection.execute(
            text("insert into STATIONS (UUID, NAME) values(:uuid, :name)"),
            {"uuid": uuid, "name": name}
        )

    def _import_means_of_transport(self, identifier: str) -> None:
        uuid = str(uuid4())
        self._means_of_transport[identifier] = uuid
        print(f"{uuid} -> {identifier}")
        self._connection.execute(
            text("insert into MEANS_OF_TRANSPORT (UUID, IDENTIFIER) values (:uuid, :identifier)"),
            {"uuid": uuid, "identifier": identifier}
        )


def import_to_database(city_plan: CityPlan) -> None:
    importer = _Importer(city_plan)
    importer.import_city_plan()
