from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from db import Line, MeansOfTransport, Station
from db import get_db
from model import JourneyLeg, JourneyPlan
from model import ItineraryEntry, LineDetails, LineInfo, LineItinerary, LineListEntry
from model import MeansOfTransportDetails, StationDetails


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


# TODO: think about the source code organization for the mapper functions
def as_line_info(line: Line) -> LineInfo:
    return LineInfo(
        label=line.label,
        means_of_transport=line.means_of_transport.identifier
    )


# TODO: think about the source code organization for the mapper functions
def as_station_details(station: Station) -> StationDetails:
    unique_lines = set()
    lines = []
    for single_edge in station.outbound_edges:
        if single_edge.line.label not in unique_lines:
            unique_lines.add(single_edge.line.label)
            lines.append(LineInfo(
                label=single_edge.line.label,
                means_of_transport=single_edge.line.means_of_transport.identifier
            ))
    return StationDetails(
        name=station.name,
        lines=lines
    )


@app.get("/stations", response_model=List[StationDetails])
async def get_station_list(filter: str = None, db: Session = Depends(get_db)):
    """
    Provides a list of stations matching with the given filter. If no filter is specified,
    all stations are returned. Asterisk can be used as wildcard in the filter. For instance,
    if the value 'S*' is specified as filter, all stations whose names start with the letter S
    will be returned.
    """
    stations = db.query(Station).filter(Station.name.like("Sch" + "%")).order_by(Station.name).all()
    return [as_station_details(single_station) for single_station in stations]


@app.get("/station", response_model=StationDetails)
async def get_station_details(name: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given name.
    """
    station = db.query(Station).filter(Station.name == name).first()
    if station is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No station with the name {name} found."
        )
    return as_station_details(station)


@app.get("/lines", response_model=List[LineListEntry])
async def get_line_list(means_of_transport: str = None, db: Session = Depends(get_db)):
    """
    Provides a list of lines with the given means of transport. If no filter is specified
    (i.e. if the parameter is omitted), all lines are returned.
    """
    return [
        LineListEntry(
            identifier="U1",
            means_of_transport="U-Bahn"
        ),
        LineListEntry(
            identifier="U2",
            means_of_transport="U-Bahn"
        ),
        LineListEntry(
            identifier="U3",
            means_of_transport="U-Bahn"
        ),
        LineListEntry(
            identifier="U4",
            means_of_transport="U-Bahn"
        ),
        LineListEntry(
            identifier="U6",
            means_of_transport="U-Bahn"
        ),
        LineListEntry(
            identifier="S1",
            means_of_transport="S-Bahn"
        ),
        LineListEntry(
            identifier="S3",
            means_of_transport="S-Bahn"
        )
    ]


@app.get("/line", response_model=LineDetails)
async def get_line_details(label: str, db: Session = Depends(get_db)):
    """
    Provides the details of the line with the given label.
    """
    return LineDetails(
        label="U3",
        means_of_transport="U-Bahn",
        direction_one_itinerary=LineItinerary(
            start="Simmering",
            destination="Ottakring",
            entries=[
                ItineraryEntry(station="Simmering", point_in_time_minutes=None),
                ItineraryEntry(station="Enkplatz", point_in_time_minutes=1),
                ItineraryEntry(station="Zippererstrasse", point_in_time_minutes=2),
            ]
        ),
        direction_two_itinerary=LineItinerary(
            start="Ottakring",
            destination="Simmering",
            entries=[

            ]
        )
    )


@app.get("/journey-plan", response_model=JourneyPlan)
async def search_journey_plan(start: str, destination: str, db: Session = Depends(get_db)):
    """
    Finds and returns a journey plan with the given start and destination.
    """
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
