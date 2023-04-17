#
# Copyright 2023 Jaroslav Chmurny
#
# This file is part of City Navigator.
#
# City Navigator is free software developed for educational and experimental
# purposes. It is licensed under the Apache License, Version 2.0 # (the
# "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from logging import getLogger
from typing import List
from uuid import uuid4

from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session

from db import Edge, Line, MeansOfTransport, Station
from db import get_db
from notifications import EventType
from notifications import get_notifier, Notifier

from .dto import LineDetails, LineInfo, LineRequest
from .dto import MeansOfTransportDetails, MeansOfTransportRequest
from .dto import StationDetails, StationRequest
from .errors import line_not_found_exception, means_of_transport_not_found_exception, station_not_found_exception
from .mapping import as_line_details_dto, as_line_info_dto, as_means_of_transport_dto, as_station_details_dto
from .mapping import create_edges_from_dto, update_line_entity_from_dto


_logger = getLogger("rest")


router = APIRouter()


@router.get("/means-of-transport", response_model=List[MeansOfTransportDetails])
async def get_means_of_transport_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all means of transport.
    """
    result_set = db.query(MeansOfTransport).order_by(MeansOfTransport.identifier).all()
    return [as_means_of_transport_dto(record) for record in result_set]


@router.get("/means-of-transport/{uuid}", response_model=MeansOfTransportDetails)
async def get_means_of_transport(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the means of transport with the given UUID.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise means_of_transport_not_found_exception(uuid)
    return as_means_of_transport_dto(record)


@router.post("/means-of-transport", response_model=MeansOfTransportDetails, status_code=status.HTTP_201_CREATED)
async def create_means_of_transport(
    request: MeansOfTransportRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Creates a new means of transport using the given request data.
    """
    means_of_transport = MeansOfTransport()
    means_of_transport.uuid = str(uuid4())
    means_of_transport.identifier = request.identifier
    db.add(means_of_transport)
    db.commit()
    _logger.debug("New means of transport (uuid = %s) inserted into the database", means_of_transport.uuid)
    notifier.send_notification(EventType.CREATED, MeansOfTransport, means_of_transport.uuid)
    return as_means_of_transport_dto(means_of_transport)


@router.put("/means-of-transport/{uuid}")
async def update_means_of_transport(
    uuid: str,
    request: MeansOfTransportRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Updates the means of transport with the given UUID, using the given request data.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise means_of_transport_not_found_exception(uuid)
    record.identifier = request.identifier
    db.commit()
    _logger.debug("Means of transport (uuid = %s) updated in the database", uuid)
    notifier.send_notification(EventType.UPDATED, MeansOfTransport, uuid)
    return as_means_of_transport_dto(record)


@router.delete("/means-of-transport/{uuid}")
async def delete_means_of_transport(
    uuid: str,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Deletes the means of transport with the given UUID.
    """
    record = db.query(MeansOfTransport).filter(MeansOfTransport.uuid == uuid).first()
    if record is None:
        raise means_of_transport_not_found_exception(uuid)
    db.delete(record)
    db.commit()
    _logger.debug("Means of transport deleted from the database")
    notifier.send_notification(EventType.DELETED, MeansOfTransport, uuid)


@router.get("/stations", response_model=List[StationDetails])
async def get_station_list(db: Session = Depends(get_db)):
    """
    Provides a list with details of all stations. The returned stations are sorted by the name,
    the order is ascending.
    """
    result_set = db.query(Station).order_by(Station.name).all()
    return [as_station_details_dto(record) for record in result_set]


@router.get("/station/{uuid}", response_model=StationDetails)
async def get_station(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise station_not_found_exception(uuid)
    return as_station_details_dto(record)


@router.post("/station", response_model=StationDetails, status_code=status.HTTP_201_CREATED)
async def create_station(
    request: StationRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Creates a new station using the given request data.
    """
    station = Station()
    station.uuid = str(uuid4())
    station.name = request.name
    db.add(station)
    db.commit()
    _logger.debug("New station (uuid = %s) inserted into the database", station.uuid)
    notifier.send_notification(EventType.CREATED, Station, station.uuid)
    return as_station_details_dto(station)


@router.put("/station/{uuid}", response_model=StationDetails)
async def update_station(
    uuid: str,
    request: StationRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Updates the station with the given UUID, using the given request data.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise station_not_found_exception(uuid)
    record.name = request.name
    db.commit()
    notifier.send_notification(EventType.UPDATED, Station, uuid)
    return as_station_details_dto(record)


@router.delete("/station/{uuid}")
async def delete_station(
    uuid: str,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Deletes the station with the given UUID.
    """
    record = db.query(Station).filter(Station.uuid == uuid).first()
    if record is None:
        raise station_not_found_exception(uuid)
    db.delete(record)
    db.commit()
    notifier.send_notification(EventType.DELETED, Station, uuid)


@router.get("/lines", response_model=List[LineInfo])
async def get_lines(db: Session = Depends(get_db)):
    result_set = db.query(Line).order_by(Line.label).all()
    return [as_line_info_dto(record) for record in result_set]


@router.get("/line/{uuid}", response_model=LineDetails)
async def get_line(uuid: str, db: Session = Depends(get_db)):
    """
    Provides the details of the line with the given UUID.
    """
    record = db.query(Line).filter(Line.uuid == uuid).first()
    if record is None:
        raise line_not_found_exception(uuid)
    return as_line_details_dto(record)


@router.post("/line", response_model=LineDetails, status_code=status.HTTP_201_CREATED)
async def create_line(
    request: LineRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Creates a new line using the given request data.
    """
    line = Line()
    line.uuid = str(uuid4())
    update_line_entity_from_dto(entity=line, dto=request)
    itinerary_one, itinerary_two = create_edges_from_dto(dto=request, line_uuid=line.uuid)
    # TODO:
    # - validate the line - terminal stops should match with the itineraries
    db.add(line)
    for single_edge in itinerary_one + itinerary_two:
        db.add(single_edge)
    db.commit()
    notifier.send_notification(EventType.CREATED, Line, line.uuid)
    return as_line_details_dto(line)


@router.put("/line/{uuid}", response_model=LineDetails)
async def update_line(
    uuid: str,
    request: LineRequest,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Updates the the line with the given UUID, using the given request data.
    """
    record = db.query(Line).filter(Line.uuid == uuid).first()
    if record is None:
        raise line_not_found_exception(uuid)
    update_line_entity_from_dto(entity=record, dto=request)
    itinerary_one, itinerary_two = create_edges_from_dto(dto=request, line_uuid=uuid)
    # TODO:
    # - validate the line - terminal stops should match with the itineraries

    # TODO:
    # - we should also update the itinerary
    # - one way to do so is to delete the entire itinerary, and create it from scratch
    # db.query(Edge).filter(Edge.line_uuid == uuid).delete()

    for single_edge in itinerary_one + itinerary_two:
        db.add(single_edge)

    db.commit()
    notifier.send_notification(EventType.UPDATED, Line, uuid)
    return as_line_details_dto(record)


@router.delete("/line/{uuid}")
async def delete_line(
    uuid: str,
    db: Session = Depends(get_db),
    notifier: Notifier = Depends(get_notifier)
):
    """
    Deletes the line with the given UUID. This operation also deletes the itinerary
    for the concerned line (both directions).
    """
    record = db.query(Line).filter(Line.uuid == uuid).first()
    if record is None:
        raise line_not_found_exception(uuid)
    db.delete(record)
    db.commit()
    notifier.send_notification(EventType.DELETED, Line, uuid)
