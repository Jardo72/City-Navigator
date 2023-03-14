from typing import List
from uuid import uuid4

from fastapi import FastAPI, status

from model import MeansOfTransportDetails, MeansOfTransportRequest
from model import StationDetails, StationRequest


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport_list():
    return [
        MeansOfTransportDetails(
            uuid=uuid4(),
            identifier="S-Bahn"
        ),
        MeansOfTransportDetails(
            uuid=uuid4(),
            identifier="U-Bahn"
        ),
        MeansOfTransportDetails(
            uuid=uuid4(),
            identifier="Tram"
        ),
        MeansOfTransportDetails(
            uuid=uuid4(),
            identifier="Bus"
        )
    ]


@app.get("/means-of-transport/{uuid}", response_model=MeansOfTransportDetails)
async def get_means_of_transport(uuid: str):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier="S-Bahn"
    )


@app.post("/means-of-transport/", response_model=MeansOfTransportDetails, status_code=status.HTTP_201_CREATED)
async def create_means_of_transport(request: MeansOfTransportRequest):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier=request.identifier
    )


@app.put("/means-of-transport/{uuid}")
async def update_means_of_transport(request: MeansOfTransportRequest):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier=request.identifier
    )


@app.delete("/means-of-transport/{uuid}")
async def delete_means_of_transport(uuid: str):
    ...


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list():
    ...


@app.get("/station/{uuid}", response_model=StationDetails)
async def get_station(uuid: str):
    ...


@app.post("/station", response_model=StationDetails, status_code=status.HTTP_201_CREATED)
async def create_station(request: StationRequest):
    ...


@app.put("/station", response_model=StationDetails)
async def update_station(request: StationRequest):
    ...


@app.delete("/station/{uuid}")
async def delete_station(uuid: str):
    ...
