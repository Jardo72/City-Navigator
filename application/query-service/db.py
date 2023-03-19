from sqlalchemy import Column, ForeignKey, Integer, String, text
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


DDL_STATEMENTS = [
    """
    CREATE TABLE MEANS_OF_TRANSPORT (
        UUID VARCHAR(36) NOT NULL PRIMARY KEY,
        IDENTIFIER VARCHAR(20) NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE STATIONS (
        UUID VARCHAR(36) NOT NULL PRIMARY KEY,
        NAME VARCHAR(50) NOT NULL UNIQUE
    );
    """,
    """
    CREATE TABLE LINES (
        UUID VARCHAR(36) NOT NULL PRIMARY KEY,
        LABEL VARCHAR(5) NOT NULL UNIQUE,
        MEANS_OF_TRANSPORT_UUID VARCHAR(36) NOT NULL,
        TERMINAL_STOP_ONE_UUID VARCHAR(36) NOT NULL,
        TERMINAL_STOP_TWO_UUID VARCHAR(36) NOT NULL,
        CONSTRAINT MEANS_OF_TRANSPORT_FK FOREIGN KEY (MEANS_OF_TRANSPORT_UUID) REFERENCES MEANS_OF_TRANSPORT(UUID),
        CHECK (TERMINAL_STOP_ONE_UUID <> TERMINAL_STOP_TWO_UUID),
        CONSTRAINT TERMINAL_STOP_ONE_FK FOREIGN KEY (TERMINAL_STOP_ONE_UUID) REFERENCES STATIONS(UUID),
        CONSTRAINT TERMINAL_STOP_TWO_FK FOREIGN KEY (TERMINAL_STOP_TWO_UUID) REFERENCES STATIONS(UUID)
    );
    """,
    """
    CREATE TABLE EDGES (
        UUID VARCHAR(36) NOT NULL PRIMARY KEY,
        START_STATION_UUID VARCHAR(36) NOT NULL,
        END_STATION_UUID VARCHAR(36) NOT NULL,
        LINE_UUID VARCHAR(36) NOT NULL,
        DISTANCE_MIN INTEGER NOT NULL,
        CONSTRAINT LINE_FK FOREIGN KEY (LINE_UUID) REFERENCES LINES(UUID),
        CHECK (DISTANCE_MIN > 0),
        CONSTRAINT START_STATION_FK FOREIGN KEY (START_STATION_UUID) REFERENCES STATIONS(UUID),
        CONSTRAINT END_STATION_FK FOREIGN KEY (END_STATION_UUID) REFERENCES STATIONS(UUID),
        CHECK (START_STATION_UUID <> END_STATION_UUID),
        CONSTRAINT EDGE_UK UNIQUE(START_STATION_UUID, END_STATION_UUID, LINE_UUID)
    );
    """
]


# conn = engine.connect()
# for statement in DDL_STATEMENTS:
#     conn.execute(text(statement))


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
