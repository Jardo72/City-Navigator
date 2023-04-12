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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config


_logger = getLogger("db")


engine = create_engine(
    url=Config.get_database_url(),
    connect_args={"check_same_thread": False},
    pool_size=20
)
_logger.info("DB engine created, URL = '%s'", Config.get_database_url())


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_logger.info("DB session maker created")


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        _logger.debug("DB session created")
        yield db
    finally:
        db.close()
        _logger.debug("DB session closed")
