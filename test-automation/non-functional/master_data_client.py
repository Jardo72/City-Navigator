from dataclasses import dataclass
from time import perf_counter
from typing import Any, Dict, List

import requests


# TODO: duplicate - eliminate
@dataclass(frozen=True, slots=True)
class Response:
    url: str
    status_code: int
    duration_millis: int
    json_data: List[Any] | Dict[str, Any]


class MasterDataClient:

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    # TODO: duplicate - eliminate
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


def main() -> None:
    client = MasterDataClient("http://localhost:8000")
    print(client.get_means_of_transport_list())


if __name__ == "__main__":
    main()
