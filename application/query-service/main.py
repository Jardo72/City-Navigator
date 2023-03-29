from contextlib import asynccontextmanager
from logging import getLogger
from sys import version as python_version

from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db import get_db
from rest import router


_logger = getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI, db: Session = Depends(get_db)):
    _logger.debug("Going to initialize the in-memory database")
    if db is None:
        _logger.error("WTF!!! DB is missing!")
    else:
        _logger.info("DB seems to be OK")

    yield
    print("Going to shutdown")


APPLICATION_NAME = "City Navigator - Master Data Service"
APPLICATION_VERSION = "0.1.0"


app = FastAPI(title=APPLICATION_NAME, lifespan=lifespan)
app.include_router(router)
Instrumentator().instrument(app).expose(app)


class VersionInfo(BaseModel):
    application_name: str = None
    application_version: str = None
    python_version: str = None


@app.get("/version", response_model=VersionInfo)
async def get_version_info():
    return VersionInfo(
        application_name=APPLICATION_NAME,
        application_version=APPLICATION_VERSION,
        python_version=python_version
    )
