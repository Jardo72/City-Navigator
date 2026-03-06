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


Base = declarative_base()


class MeansOfTransport(Base):
    __tablename__ = "t_means_of_transport"
    uuid = Column("uuid", String, primary_key=True)
    identifier = Column("identifier", String(length=20), nullable=False)


class Station(Base):
    __tablename__ = "t_stations"
    uuid = Column("uuid", String, primary_key=True)
    name = Column("name", String(length=50), nullable=False)
    outbound_edges = relationship("Edge", foreign_keys="Edge.start_station_uuid", back_populates="start_station")


class Line(Base):
    __tablename__ = "t_lines"
    uuid = Column("uuid", String, primary_key=True, index=True)
    label = Column("label", String, nullable=False)
    means_of_transport_uuid = Column("means_of_transport_uuid", String, ForeignKey("t_means_of_transport.uuid"), nullable=False)
    means_of_transport = relationship("MeansOfTransport", foreign_keys="Line.means_of_transport_uuid")
    terminal_stop_one_uuid = Column("terminal_stop_one_uuid", String, ForeignKey("t_stations.uuid"), nullable=False)
    terminal_stop_two_uuid = Column("terminal_stop_two_uuid", String, ForeignKey("t_stations.uuid"), nullable=False)
    terminal_stop_one = relationship("Station", foreign_keys="Line.terminal_stop_one_uuid")
    terminal_stop_two = relationship("Station", foreign_keys="Line.terminal_stop_two_uuid")


class Edge(Base):
    __tablename__ = "t_edges"
    uuid = Column("uuid", String, primary_key=True)
    distance_min = Column("distance_min", Integer, nullable=False)
    start_station_uuid = Column("start_station_uuid", String, ForeignKey("t_stations.uuid"), nullable=False)
    end_station_uuid = Column("end_station_uuid", String, ForeignKey("t_stations.uuid"), nullable=False)
    line_uuid = Column("line_uuid", String, ForeignKey("t_lines.uuid"), nullable=False)
    start_station = relationship("Station", foreign_keys="Edge.start_station_uuid", back_populates="outbound_edges")
    end_station = relationship("Station", foreign_keys="Edge.end_station_uuid")
    line = relationship("Line", foreign_keys="Edge.line_uuid")
