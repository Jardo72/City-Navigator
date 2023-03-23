from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, List

import requests


@dataclass(frozen=True, slots=True)
class Response:
    url: str
    status_code: int
    duration_millis: int
    json_data: List[Any] | Dict[str, Any]


class QueryServiceClient:

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def _get_request(self, path: str, params: Dict[str, str] = None) -> Response:
        start_time = perf_counter()
        response = requests.get(url=f"{self._base_url}{path}", params=params)
        duration_sec = perf_counter() - start_time
        return Response(
            url=response.request.url,
            status_code=response.status_code,
            duration_millis=round(1000 * duration_sec),
            json_data=response.json()
        )

    def get_means_of_transport_list(self) -> Response:
        return self._get_request("/means-of-transport")

    def get_station_list(self) -> Response:
        return self._get_request("/stations")

    def get_station_details(self, name: str) -> Response:
        return self._get_request("/station", params={"name": name})

    def get_line_list(self) -> Response:
        return self._get_request("/lines")

    def get_line_details(self, label: str) -> Response:
        return self._get_request("/line", params={"label": label})

    def search_journey_plan(self, start: str, destination: str) -> Response:
        return self._get_request("/journey-plan", params={"start": start, "destination": destination})


def main() -> None:
    client = QueryServiceClient("http://localhost:8000")

    print("Stations")
    for _ in range(20):
        response = client.get_station_list()
        print(f"Status code = {response.status_code}, duration = {response.duration_millis} millis")

    print()
    print("Lines")
    for _ in range(20):
        response = client.get_line_list()
        print(f"Status code = {response.status_code}, duration = {response.duration_millis} millis")

    print()
    print("Jounrey plans")
    journeys = [
        ("Simmering", "Strebersdorf"),
        ("Karlsplatz", "Alte Donau"),
        ("Am Tabor", "Herrengasse"),
        ("Schoenbrunn", "Heiligenstadt"),
        ("Penzing", "Rauscherstrasse"),
    ]
    for start, destination in journeys:
        response = client.search_journey_plan(start, destination)
        print(f"Status code = {response.status_code}, duration = {response.duration_millis} millis")


if __name__ == "__main__":
    main()
