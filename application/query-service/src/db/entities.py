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

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


_Base = declarative_base()


class MeansOfTransport(_Base):
    __tablename__ = "MEANS_OF_TRANSPORT"
    uuid = Column("UUID", String, primary_key=True)
    identifier = Column("IDENTIFIER", String(length=20), nullable=False)
    lines = relationship("Line", foreign_keys="Line.means_of_transport_uuid", back_populates="means_of_transport")


class Station(_Base):
    __tablename__ = "STATIONS"
    uuid = Column("UUID", String, primary_key=True)
    name = Column("NAME", String(length=50), nullable=False)
    outbound_edges = relationship("Edge", foreign_keys="Edge.start_station_uuid", back_populates="start_station")


class Line(_Base):
    __tablename__ = "LINES"
    uuid = Column("UUID", String, primary_key=True, index=True)
    label = Column("LABEL", String, nullable=False)
    means_of_transport_uuid = Column("MEANS_OF_TRANSPORT_UUID", String, ForeignKey("MEANS_OF_TRANSPORT.UUID"), nullable=False)
    means_of_transport = relationship("MeansOfTransport", foreign_keys="Line.means_of_transport_uuid", back_populates="lines")
    terminal_stop_one_uuid = Column("TERMINAL_STOP_ONE_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    terminal_stop_two_uuid = Column("TERMINAL_STOP_TWO_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    terminal_stop_one = relationship("Station", foreign_keys="Line.terminal_stop_one_uuid")
    terminal_stop_two = relationship("Station", foreign_keys="Line.terminal_stop_two_uuid")


class Edge(_Base):
    __tablename__ = "EDGES"
    uuid = Column("UUID", String, primary_key=True)
    distance_min = Column("DISTANCE_MIN", Integer, nullable=False)
    start_station_uuid = Column("START_STATION_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    end_station_uuid = Column("END_STATION_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    line_uuid = Column("LINE_UUID", String, ForeignKey("LINES.UUID"), nullable=False)
    start_station = relationship("Station", foreign_keys="Edge.start_station_uuid", back_populates="outbound_edges")
    end_station = relationship("Station", foreign_keys="Edge.end_station_uuid")
    line = relationship("Line", foreign_keys="Edge.line_uuid")
