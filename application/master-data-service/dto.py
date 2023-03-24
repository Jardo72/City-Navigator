from typing import List

from pydantic import BaseModel


class VersionInfo(BaseModel):
    application_name: str = None
    application_version: str = None
    python_version: str = None


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
    terminal_stop_one: StationDetails = None
    terminal_stop_two: StationDetails = None
    direction_one_itinerary: List[ItineraryEntry] = None
    direction_two_itinerary: List[ItineraryEntry] = None


class LineRequest(BaseModel):
    label: str = None
    means_of_transport_uuid: str = None
    terminal_stop_one_uuid: str = None
    terminal_stop_two_uuid: str = None
