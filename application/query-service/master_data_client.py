import requests


def _message_from(response: requests.Response) -> str:
    status_code = response.status_code
    reason = response.reason
    url = response.request.url
    return (
        f"Failed to GET {url} (status code = {status_code}, reason = '{reason}').\n"
        f"Response body:\n{response.text if response.text else ''}"
    )


class MasterDataClientException(Exception):

    def __init__(self, response: requests.Response) -> None:
        super().__init__(_message_from(response))


class MasterDataClient:

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    def get_means_of_transport(self):
        response = requests.get(f"{self._base_url}/means-of-transport")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        return response.json()

    def get_stations(self):
        response = requests.get(f"{self._base_url}/stations")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        return response.json()

    def get_lines(self):
        response = requests.get(f"{self._base_url}/lines")
        if response.status_code != 200:
            raise MasterDataClientException(response)
        return response.json()


def main() -> None:
    client = MasterDataClient("http://localhost:8000")
    print(client.get_stations())
    print(client.get_lines())


if __name__ == "__main__":
    main()
