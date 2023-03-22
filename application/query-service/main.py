from sys import version as python_version
from typing import List

from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.orm import Session

from db import Line, MeansOfTransport, Station
from db import get_db
from dto import JourneyPlan
from dto import LineDetails, LineInfo
from dto import MeansOfTransportDetails, StationDetails
from dto import VersionInfo
from mapping import as_journey_plan, as_line_details, as_line_info, as_means_of_transport_details, as_station_details
from search import find_shortest_path
from util import line_not_found_exception, station_not_found_exception


APPLICATION_NAME = "City Navigator - Master Data Service"
APPLICATION_VERSION = "0.1.0"


app = FastAPI(title=APPLICATION_NAME)
Instrumentator().instrument(app).expose(app)


@app.get("/version", response_model=List[VersionInfo])
async def get_version_indo():
    return VersionInfo(
        applcation_name=APPLICATION_NAME,
        application_version=APPLICATION_VERSION,
        python_version=python_version
    )


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport(db: Session = Depends(get_db)):
    """
    Provides a list of all means of transport.
    """
    means_of_transport = db.query(MeansOfTransport).all()
    return [as_means_of_transport_details(single_means_of_transport) for single_means_of_transport in means_of_transport]


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list(filter: str = None, db: Session = Depends(get_db)):
    """
    Provides a list of stations matching with the given filter. If no filter is specified,
    all stations are returned. Asterisk can be used as wildcard in the filter. For instance,
    if the value 'S*' is specified as filter, all stations whose names start with the letter S
    will be returned.
    """
    if filter is None:
        stations = db.query(Station).order_by(Station.name).all()
    else:
        filter = filter.replace("*", "%")
        stations = db.query(Station).filter(Station.name.like(filter)).order_by(Station.name).all()
    return [as_station_details(single_station) for single_station in stations]


@app.get("/station", response_model=StationDetails)
async def get_station_details(name: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given name.
    """
    station = db.query(Station).filter(Station.name == name).first()
    if station is None:
        raise station_not_found_exception(name)
    return as_station_details(station)


@app.get("/lines", response_model=List[LineInfo])
async def get_line_list(means_of_transport: str = None, db: Session = Depends(get_db)):
    """
    Provides a list of lines with the given means of transport. If no filter is specified
    (i.e. if the parameter is omitted), all lines are returned.
    """
    if means_of_transport is None:
        lines = db.query(Line).order_by(Line.label).all()
    else:
        filter = db.query(MeansOfTransport).filter(MeansOfTransport.identifier == means_of_transport).first()
        lines = db.query(Line).filter(Line.means_of_transport == filter).order_by(Line.label).all()
    return [as_line_info(single_line) for single_line in lines]


@app.get("/line", response_model=LineDetails)
async def get_line_details(label: str, db: Session = Depends(get_db)):
    """
    Provides the details of the line with the given label.
    """
    line = db.query(Line).filter(Line.label == label).first()
    if not line:
        raise line_not_found_exception(label)
    return as_line_details(line)


@app.get("/journey-plan", response_model=JourneyPlan)
async def search_journey_plan(start: str, destination: str, db: Session = Depends(get_db)):
    """
    Finds and returns a journey plan with the given start and destination.
    """
    start_station = db.query(Station).filter(Station.name == start).first()
    if start_station is None:
        raise station_not_found_exception(start)
    destination_station = db.query(Station).filter(Station.name == destination).first()
    if destination_station is None:
        raise station_not_found_exception(destination)
    search_result = find_shortest_path(start_station, destination_station)
    return as_journey_plan(search_result)
