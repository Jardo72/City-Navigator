from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, status
from sqlalchemy.orm import Session

from db import MeansOfTransport, Station
from db import get_db
from model import MeansOfTransportDetails, MeansOfTransportRequest
from model import StationDetails, StationRequest


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport_list(db: Session = Depends(get_db)):
    result_set = db.query(MeansOfTransport).order_by(MeansOfTransport.identifier).all()
    return [MeansOfTransportDetails(uuid=record.uuid, identifier=record.identifier) for record in result_set]


@app.get("/means-of-transport/{uuid}", response_model=MeansOfTransportDetails)
async def get_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    return MeansOfTransportDetails(uuid=record.uuid, identifier=record.identifier)


@app.post("/means-of-transport/", response_model=MeansOfTransportDetails, status_code=status.HTTP_201_CREATED)
async def create_means_of_transport(request: MeansOfTransportRequest, db: Session = Depends(get_db)):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier=request.identifier
    )


@app.put("/means-of-transport/{uuid}")
async def update_means_of_transport(request: MeansOfTransportRequest, db: Session = Depends(get_db)):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier=request.identifier
    )


@app.delete("/means-of-transport/{uuid}")
async def delete_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    ...


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list(db: Session = Depends(get_db)):
    result_set = db.query(Station).order_by(Station.name).all()
    return [StationDetails(uuid=record.uuid, name=record.name) for record in result_set]


@app.get("/station/{uuid}", response_model=StationDetails)
async def get_station(uuid: str, db: Session = Depends(get_db)):
    record = db.query(Station).filter(Station.uuid == uuid).first()
    return StationDetails(uuid=record.uuid, name=record.name)


@app.post("/station", response_model=StationDetails, status_code=status.HTTP_201_CREATED)
async def create_station(request: StationRequest):
    ...


@app.put("/station", response_model=StationDetails)
async def update_station(request: StationRequest):
    ...


@app.delete("/station/{uuid}")
async def delete_station(uuid: str):
    ...
