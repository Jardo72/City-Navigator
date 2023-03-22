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
        return response.json()

    def get_stations(self):
        response = requests.get(f"{self._base_url}/stations")
        if response.status_code != 200:
            ...
        return response.json()

    def get_lines(self):
        response = requests.get(f"{self._base_url}/lines")
        if response.status_code != 200:
            ...
        return response.json()


def main() -> None:
    client = MasterDataClient("http://localhost:8000")
    print(client.get_stations())
    ...


if __name__ == "__main__":
    main()
