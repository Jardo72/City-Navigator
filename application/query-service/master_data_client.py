import requests


class MasterDataClientException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MasterDataClient:

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def get_means_of_transport(self):
        response = requests.get(f"{self._base_url}/means_of_transport")
        if response.status_code != 200:
            ...

    def get_stations(self):
        response = requests.get(f"{self._base_url}/stations")
        if response.status_code != 200:
            ...

    def get_lines(self):
        response = requests.get(f"{self._base_url}/lines")
        if response.status_code != 200:
            ...
