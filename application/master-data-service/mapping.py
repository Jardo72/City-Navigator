from db import Line, MeansOfTransport, Station
from dto import MeansOfTransportDetails, StationDetails


def as_means_of_transport(means_of_transport: MeansOfTransport) -> MeansOfTransportDetails:
    return MeansOfTransportDetails(
        uuid=means_of_transport.uuid,
        identifier=means_of_transport.identifier
    )


def as_station_details(station: Station) -> StationDetails:
    return StationDetails(
        uuid=station.uuid,
        name=station.name
    )
