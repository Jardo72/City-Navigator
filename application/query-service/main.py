from typing import List

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from model import JourneyLeg, JourneyPlan
from model import ItineraryEntry, LineDetails, LineItinerary, LineListEntry
from model import MeansOfTransport, StationDetails


# see https://fastapi.tiangolo.com/advanced/events/


# see https://stackoverflow.com/questions/62333314/python-sqlalchemy-in-memory-database-connect
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False}
)
print("DB engine created")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


conn = engine.connect()
conn.execute(text(
"""
CREATE TABLE MEANS_OF_TRANSPORT (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    IDENTIFIER VARCHAR(20) NOT NULL UNIQUE
);
"""
))
conn.execute(text(
"""
CREATE TABLE NODES (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(50) NOT NULL UNIQUE
);
"""
))


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransport])
async def get_means_of_transport(db: Session = Depends(get_db)):
    """
    Provides a list of all means of transport.
    """
    return [
        MeansOfTransport(
            identifier="S-Bahn",
            lines=[
                "S1",
                "S3"
            ]
        ),
        MeansOfTransport(
            identifier="U-Bahn",
            lines=[
                "U1",
                "U2",
                "U3",
                "U4",
                "U6"
            ]
        )
    ]


@app.get("/stations", response_model=List[str])
async def get_station_list(filter: str = None, db: Session = Depends(get_db)):
    """
    Provides a list of stations matching with the given filter. If no filter is specified,
    all stations are returned. Asterisk can be used as wildcard in the filter. For instance,
    if the value 'S*' is specified as filter, all stations whose names start with the letter S
    will be returned.
    """
    return [
        "Alte Donau",
        "Kagran",
        "Meidling",
        "Simmering",
        "Zippererstrasse"
    ]


@app.get("/station", response_model=StationDetails)
async def get_station_details(name: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given name.
    """
    return StationDetails(
        name="Wien Mitte",
        lines=[]
    )


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
