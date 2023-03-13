from typing import List

from fastapi import FastAPI

from model import JourneyPlan, LineDetails, LineItinerary, LineListEntry, MeansOfTransport, StationDetails


app = FastAPI()


@app.get("/means-of-transport", response_model=List[MeansOfTransport])
async def get_means_of_transport():
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
async def get_station_list(filter: str = None):
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
async def get_station_details(name: str):
    """
    Provides the details of the station with the given name.
    """
    return StationDetails(
        name="Wien Mitte",
        lines=[]
    )


@app.get("/lines", response_model=List[LineListEntry])
async def get_line_list(means_of_transport: str = None):
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
async def get_line_details(identifier: str):
    """
    Provides the details of the line with the given identifier.
    """
    return LineDetails(
        identifier="U3",
        means_of_transport="U-Bahn",
        direction_one_itinerary=LineItinerary(
            start="",
            destination="",
            entries=[]
        ),
        direction_two_itinerary=LineItinerary(
            start="",
            destination="",
            entries=[]
        )
    )


@app.get("/journey-plan", response_model=JourneyPlan)
async def search_journey_plan(start: str, destination: str):
    """
    Finds and returns a journey plan with the given start and destination.
    """
    return JourneyPlan(
        start="",
        destination="",
        legs=[]
    )
