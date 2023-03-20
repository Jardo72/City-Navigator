from db import Line, MeansOfTransport, Station
from dto import LineDetails, MeansOfTransportDetails, StationDetails


def as_line_details(line: Line) -> LineDetails:
    return LineDetails(
        uuid=line.uuid,
        label=line.label,
        means_of_transport=line.means_of_transport.identifier,
        terminal_stop_one=line.terminal_stop_one.name,
        terminal_stop_two=line.terminal_stop_two.name
    )


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
