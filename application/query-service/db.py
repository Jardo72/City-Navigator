from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# see https://stackoverflow.com/questions/62333314/python-sqlalchemy-in-memory-database-connect
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


# conn = engine.connect()
# conn.execute(text(
# """
# CREATE TABLE MEANS_OF_TRANSPORT (
#     ID INTEGER PRIMARY KEY AUTOINCREMENT,
#     IDENTIFIER VARCHAR(20) NOT NULL UNIQUE
# );
# """
# ))
# conn.execute(text(
# """
# CREATE TABLE NODES (
#     ID INTEGER PRIMARY KEY AUTOINCREMENT,
#     NAME VARCHAR(50) NOT NULL UNIQUE
# );
# """
# ))


class MeansOfTransport(Base):
    __tablename__ = "MEANS_OF_TRANSPORT"
    uuid = Column("UUID", String, primary_key=True)
    identifier = Column("IDENTIFIER", String(length=20), nullable=False)
    lines = relationship("Line", foreign_keys="Line.means_of_transport_uuid", back_populates="means_of_transport")


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
    means_of_transport = relationship("MeansOfTransport", foreign_keys="Line.means_of_transport_uuid", back_populates="lines")
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

        means_of_transport = db.query(MeansOfTransport).all()
        for single_means_of_transport in means_of_transport:
            print(f"uuid={single_means_of_transport.uuid}, name={single_means_of_transport.identifier}")
            for single_line in single_means_of_transport.lines:
                print(f"  - {single_line.label}")
            print()
    finally:
        db.close()


if __name__ == "__main__":
    main()
