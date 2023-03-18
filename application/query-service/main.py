from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db import Line, MeansOfTransport, Station
from db import get_db
from dto import JourneyLeg, JourneyPlan
from dto import LineDetails, LineInfo
from dto import MeansOfTransportDetails, StationDetails
from mapping import as_line_details, as_line_info, as_station_details
from util import line_not_found_exception, station_not_found_exception


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport(db: Session = Depends(get_db)):
    """
    Provides a list of all means of transport.
    """
    means_of_transport = db.query(MeansOfTransport).all()
    result = []
    for single_means_of_transport in means_of_transport:
        line_names=[line.label for line in single_means_of_transport.lines]
        line_names.sort()
        result.append(MeansOfTransportDetails(
            identifier=single_means_of_transport.identifier,
            lines=line_names
        ))
    return result


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
    start_station = db.query().filter(Station.name == start).first()
    if start_station is None:
        raise station_not_found_exception(start)
    destination_station = db.query().filter(Station.name == destination).first()
    if destination_station is None:
        raise station_not_found_exception(destination)
    return JourneyPlan(
        start="Simmering",
        destination="Praterstern",
        legs=[
            JourneyLeg(
                start="Simmering",
                destination="Landstrasse",
                means_of_transport="U-Bahn",
                line="U3",
                stop_count=7,
                duration_minutes=13
            ),
            JourneyLeg(
                start="Landstrasse",
                destination="Praterstern",
                means_of_transport="S-Bahn",
                line="S1",
                stop_count=2,
                duration_minutes=3
            )
        ]
    )
