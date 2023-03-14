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
