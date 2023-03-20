from typing import List
from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi import status
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from db import Line, MeansOfTransport, Station
from db import get_db
from dto import LineDetails
from dto import MeansOfTransportDetails, MeansOfTransportRequest
from dto import StationDetails, StationRequest
from mapping import as_line_details, as_means_of_transport, as_station_details
from util import line_not_found_exception, means_of_transport_not_found_exception, station_not_found_exception


app = FastAPI(title="City Navigator - Master Data Service")
Instrumentator().instrument(app).expose(app)


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all means of transport.
    """
    result_set = db.query(MeansOfTransport).order_by(MeansOfTransport.identifier).all()
    return [as_means_of_transport(record) for record in result_set]


@app.get("/means-of-transport/{uuid}", response_model=MeansOfTransportDetails)
async def get_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the means of transport with the given UUID.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise means_of_transport_not_found_exception(uuid)
    return as_means_of_transport(record)


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
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise means_of_transport_not_found_exception(uuid)
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
        raise means_of_transport_not_found_exception(uuid)
    db.delete(record)
    db.commit()


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all stations. The returned stations are sorted by the name,
    the order is ascending.
    """
    result_set = db.query(Station).order_by(Station.name).all()
    return [as_station_details(record) for record in result_set]


@app.get("/station/{uuid}", response_model=StationDetails)
async def get_station(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise station_not_found_exception(uuid)
    return as_station_details(record)


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
    if record is None:
        raise station_not_found_exception(uuid)
    record.name = request.name
    db.commit()


@app.delete("/station/{uuid}")
async def delete_station(uuid: str, db: Session = Depends(get_db)):
    """
    Deletes the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise station_not_found_exception(uuid)
    db.delete(record)
    db.commit()


@app.get("/lines", response_model=List[LineDetails])
async def get_lines(db: Session = Depends(get_db)):
    result_set = db.query(Line).order_by(Line.label).all()
    return [as_line_details(record) for record in result_set]


@app.get("/line/{uuid}", response_model=LineDetails)
async def get_line(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the line with the given UUID.
    """
    record = db.query(Line).filter(Line.uuid == uuid).first()
    if record is None:
        raise line_not_found_exception(uuid)
    return LineDetails(
        uuid=record.uuid,
        label=record.label,
        means_of_transport=record.means_of_transport.identifier,
        terminal_stop_one=record.terminal_stop_one.name,
        terminal_stop_two=record.terminal_stop_two.name
    )


@app.post("/line")
async def create_line(db: Session = Depends(get_db)):
    ...


@app.put("/line/{uuid}")
async def update_line(uuid: str, db: Session = Depends(get_db)):
    ...


@app.delete("/line/{uuid}")
async def delete_line(uuid: str, db: Session = Depends(get_db)):
    """
    Deletes the line with the given UUID. This operation also deletes the itinerary
    for the concerned line (both directions).
    """
    record = db.query(Line).filter(Line.uuid == uuid).first()
    if record is None:
        raise line_not_found_exception(uuid)
    db.delete(record)
    db.commit()
