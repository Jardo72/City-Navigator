from typing import List, Optional
from pydantic import BaseModel


class JourneyLeg(BaseModel):
    start: str = None
    destination: str = None
    means_of_transport: str = None
    line: str = None
    stop_count: int = None
    duration_minutes: int = None


class JourneyPlan(BaseModel):
    start: str = None
    destination: str = None
    legs: List[JourneyLeg] = None


class ItineraryEntry(BaseModel):
    station: str = None
    point_in_time_minutes: Optional[int] = None


class LineItinerary(BaseModel):
    start: str = None
    destination: str = None
    entries: List[ItineraryEntry] = None


class LineDetails(BaseModel):
    label: str = None
    means_of_transport: str = None
    direction_one_itinerary: LineItinerary = None
    direction_two_itinerary: LineItinerary = None


class MeansOfTransportDetails(BaseModel):
    identifier: str = None
    lines: List[str] = None


class StationDetails(BaseModel):
    name: str = None
    lines: List[LineDetails] = None


class LineListEntry(BaseModel):
    identifier: str = None
    means_of_transport: str = None
