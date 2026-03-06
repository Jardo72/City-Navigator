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

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


_logger = getLogger("db")


_engine = create_engine(
    url="sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    # pool_size=20
)
_logger.info("DB engine created")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
_logger.info("DB session maker created")


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        _logger.debug("DB session created (get_db)")
        yield db
    finally:
        db.close()
        _logger.debug("DB session closed")


def get_db_session() -> SessionLocal:
    result = SessionLocal()
    _logger.debug("DB session created (get_db_session)")
    return result


_DDL_STATEMENTS = [
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
        CONSTRAINT LINE_FK FOREIGN KEY (LINE_UUID) REFERENCES LINES(UUID) ON DELETE CASCADE,
        CHECK (DISTANCE_MIN > 0),
        CONSTRAINT START_STATION_FK FOREIGN KEY (START_STATION_UUID) REFERENCES STATIONS(UUID),
        CONSTRAINT END_STATION_FK FOREIGN KEY (END_STATION_UUID) REFERENCES STATIONS(UUID),
        CHECK (START_STATION_UUID <> END_STATION_UUID),
        CONSTRAINT EDGE_UK UNIQUE(START_STATION_UUID, END_STATION_UUID, LINE_UUID)
    );
    """
]


with _engine.connect() as conn:
    _logger.info("Going to create DB schema")
    for statement in _DDL_STATEMENTS:
        _logger.debug("Going to execute DDL statement:\n%s", statement)
        conn.execute(text(statement))
    conn.commit()
    _logger.info("DB schema created")
