from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from db import Line, MeansOfTransport, Station
from db import get_db
from dto import LineDetails
from dto import MeansOfTransportDetails, MeansOfTransportRequest
from dto import StationDetails, StationRequest


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all means of transport.
    """
    result_set = db.query(MeansOfTransport).order_by(MeansOfTransport.identifier).all()
    return [MeansOfTransportDetails(uuid=record.uuid, identifier=record.identifier) for record in result_set]


@app.get("/means-of-transport/{uuid}", response_model=MeansOfTransportDetails)
async def get_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the means of transport with the given UUID.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    return MeansOfTransportDetails(uuid=record.uuid, identifier=record.identifier)


@app.post("/means-of-transport/", response_model=MeansOfTransportDetails, status_code=status.HTTP_201_CREATED)
async def create_means_of_transport(request: MeansOfTransportRequest, db: Session = Depends(get_db)):
    means_of_transport = MeansOfTransport()
    means_of_transport.uuid = str(uuid4())
    means_of_transport.identifier = request.identifier
    db.add(means_of_transport)
    db.commit()
    return MeansOfTransportDetails(
        uuid=means_of_transport.uuid,
        identifier=request.identifier
    )


@app.put("/means-of-transport/{uuid}")
async def update_means_of_transport(uuid: str, request: MeansOfTransportRequest, db: Session = Depends(get_db)):
    return MeansOfTransportDetails(
        uuid=uuid4(),
        identifier=request.identifier
    )


@app.delete("/means-of-transport/{uuid}")
async def delete_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    """
    Deletes the means of transport with the given UUID.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Means of transport with the UUID {uuid} not found."
        )
    db.delete(record)
    db.commit()


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all stations. The returned stations are sorted by the name,
    the order is ascending.
    """
    result_set = db.query(Station).order_by(Station.name).all()
    return [StationDetails(uuid=record.uuid, name=record.name) for record in result_set]


@app.get("/station/{uuid}", response_model=StationDetails)
async def get_station(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with the UUID {uuid} not found."
        )
    return StationDetails(uuid=record.uuid, name=record.name)


@app.post("/station", response_model=StationDetails, status_code=status.HTTP_201_CREATED)
async def create_station(request: StationRequest, db: Session = Depends(get_db)):
    station = Station()
    station.uuid = str(uuid4())
    station.name = request.name
    db.add(station)
    db.commit()
    return StationDetails(uuid=station.uuid, name=station.name)


@app.put("/station/{uuid}", response_model=StationDetails)
async def update_station(uuid: str, request: StationRequest, db: Session = Depends(get_db)):
    record = db.query(Station).filter(Station.uuid == uuid).first()
    record.name = request.name
    db.commit()


@app.delete("/station/{uuid}")
async def delete_station(uuid: str, db: Session = Depends(get_db)):
    """
    Deletes the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    db.delete(record)
    db.commit()


@app.get("/lines", response_model=List[LineDetails])
async def get_lines(db: Session = Depends(get_db)):
    result_set = db.query(Line).order_by(Line.label).all()
    result = []
    for record in result_set:
        result.append(LineDetails(
            uuid=record.uuid,
            label=record.label,
            means_of_transport=record.means_of_transport.identifier,
            terminal_stop_one=record.terminal_stop_one.name,
            terminal_stop_two=record.terminal_stop_two.name
        ))
    return result
