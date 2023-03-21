from pydantic import BaseModel


class MeansOfTransportDetails(BaseModel):
    uuid: str = None
    identifier: str = None
    presentation_color: str = None


class MeansOfTransportRequest(BaseModel):
    identifier: str = None
    presentation_color: str = None


class StationDetails(BaseModel):
    uuid: str = None
    name: str = None


class StationRequest(BaseModel):
    name: str = None


class LineInfo(BaseModel):
    uuid: str = None
    label: str = None
    means_of_transport: str = None
    terminal_stop_one: str = None
    terminal_stop_two: str = None


class ItineraryEntry(BaseModel):
    station: StationDetails = None
    point_in_time_minutes: int = None


class LineDetails(BaseModel):
    uuid: str = None
    label: str = None
    means_of_transport: str = None
    terminal_stop_one: str = None
    terminal_stop_two: str = None


class LineRequest(BaseModel):
    label: str = None
    means_of_transport_uuid: str = None
    terminal_stop_one_uuid: str = None
    terminal_stop_two_uuid: str = None
