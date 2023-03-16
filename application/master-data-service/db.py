from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()


class MeansOfTransport(Base):
    __tablename__ = "MEANS_OF_TRANSPORT"
    uuid = Column("UUID", String, primary_key=True)
    identifier = Column("IDENTIFIER", String(length=20), nullable=False)


class Station(Base):
    __tablename__ = "STATIONS"
    uuid = Column("UUID", String, primary_key=True)
    name = Column("NAME", String(length=50), nullable=False)
    outbound_edges = relationship("Edge", foreign_keys="Edge.start_station_uuid", back_populates="start_station")


class Line(Base):
    __tablename__ = "LINES"
    uuid = Column("UUID", String, primary_key=True, index=True)
    label = Column("LABEL", String, nullable=False)
    means_of_transport_uuid = Column("MEANS_OF_TRANSPORT_UUID", String, ForeignKey("MEANS_OF_TRANSPORT.UUID"), nullable=False)
    means_of_transport = relationship("MeansOfTransport", foreign_keys="Line.means_of_transport_uuid")
    terminal_stop_one_uuid = Column("TERMINAL_STOP_ONE_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    terminal_stop_two_uuid = Column("TERMINAL_STOP_TWO_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    terminal_stop_one = relationship("Station", foreign_keys="Line.terminal_stop_one_uuid")
    terminal_stop_two = relationship("Station", foreign_keys="Line.terminal_stop_two_uuid")


class Edge(Base):
    __tablename__ = "EDGES"
    uuid = Column("UUID", String, primary_key=True)
    distance_min = Column("DISTANCE_MIN", Integer, nullable=False)
    start_station_uuid = Column("START_STATION_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    end_station_uuid = Column("END_STATION_UUID", String, ForeignKey("STATIONS.UUID"), nullable=False)
    line_uuid = Column("LINE_UUID", String, ForeignKey("LINES.UUID"), nullable=False)
    start_station = relationship("Station", foreign_keys="Edge.start_station_uuid", back_populates="outbound_edges")
    end_station = relationship("Station", foreign_keys="Edge.end_station_uuid")
    line = relationship("Line", foreign_keys="Edge.line_uuid")


def main() -> None:
    try:
        db = SessionLocal()

        print()
        print("Means of transport")
        means_of_transport = db.query(MeansOfTransport).all()
        for single_means_of_transport in means_of_transport:
            print(f"uuid={single_means_of_transport.uuid}, name={single_means_of_transport.identifier}")

        print()
        print("Stations")
        stations = db.query(Station).order_by(Station.name).limit(10).all()
        for single_station in stations:
            print(f"uuid={single_station.uuid}, name={single_station.name}")

        print()
        print("Station by name")
        station = db.query(Station).filter(Station.name == "Simmering").first()
        print(f"uuid={station.uuid}, name={station.name}")

        print()
        print("Station with filter")
        stations = db.query(Station).filter(Station.name.like("Sch" + "%")).order_by(Station.name).all()
        for single_station in stations:
            print(f"uuid={single_station.uuid}, name={single_station.name}")

        print()
        print("Lines")
        lines = db.query(Line).all()
        for single_line in lines:
            print(f"label={single_line.label} ({single_line.means_of_transport.identifier}) {single_line.terminal_stop_one.name} - {single_line.terminal_stop_two.name} ")

        print()
        print("Edges")
        edges = db.query(Edge).limit(10).all()
        for single_edge in edges:
            print(f"{single_edge.line.label}: {single_edge.start_station.name} -> {single_edge.end_station.name} ({single_edge.distance_min} min)")
    
        print()
        print("Line itinerary")
        line = db.query(Line).filter(Line.label == "U3").first()
        print(f"{line.label}: {line.terminal_stop_one.name} - {line.terminal_stop_two.name}")
        while True:
            ...
    finally:
        db.close()


if __name__ == "__main__":
    main()
