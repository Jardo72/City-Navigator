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

from json import loads
from logging import getLogger
from threading import Thread
from typing import Any, Dict

from prometheus_client import Counter
from redis import Redis

from config import Config
from db import get_db_session
from master_data import AbstractSynchronizer, LineSynchronizer, MeansOfTransportSynchronizer, StationSynchronizer
from master_data import MasterDataClient

from .dto import Entity, Event, EventType


_logger = getLogger("notifications")


error_counter = Counter(
    name="query_service_notification_errors_total",
    documentation="Number of errors encountered by query service when processing notifications from master data service",
    labelnames=["event_type", "entity"]
)

def _is_irrelevant(message: Dict[str, Any]) -> bool:
    if message is None:
        return True
    if message["type"] != "message":
        return True
    if message["channel"] != Config.get_redis_channel():
        return True
    return False


def _normalize(value: str) -> str:
    result = ""
    for index, ch in enumerate(value):
        if index != 0 and ch.isupper():
            result += "_" + ch
        elif ch.islower():
            result += ch.upper()
        else:
            result += ch
    return result


def _extract_event_details(message: Dict[str, Any]) -> Event:
    try:
        json_data = loads(message["data"])
        event_type = json_data["event_type"]
        entity = json_data["entity"]
        uuid = json_data["uuid"]
        return Event(
            event_type=EventType[event_type.upper()],
            entity=Entity[_normalize(entity)],
            uuid=uuid
        )
    except Exception:
        error_counter.labels(event_type="unknown", entity="unknown").inc()
        _logger.exception("Failed to extract event details from %s", message)
        return None


def _create_synchronizer(entity: Entity) -> AbstractSynchronizer:
    _logger.debug("Going to create synchronizer for entity %s", entity)
    client = MasterDataClient(Config.get_master_data_service_base_url())
    db = get_db_session()
    if entity is Entity.LINE:
        return LineSynchronizer(db, client)
    if entity is Entity.MEANS_OF_TRANSPORT:
        return MeansOfTransportSynchronizer(db, client)
    if entity is Entity.STATION:
        return StationSynchronizer(db, client)
    _logger.error("Unable to create synchronizer for entity %s", entity)


def _process_event(event: Event) -> None:
    try:
        with _create_synchronizer(event.entity) as synchronizer:
            _logger.debug("Going to use %s to synchronize data", type(synchronizer))
            if event.event_type == EventType.CREATED:
                synchronizer.create_entity(event.uuid)
            elif event.event_type == EventType.UPDATED:
                synchronizer.update_entity(event.uuid)
            elif event.event_type == EventType.DELETED:
                synchronizer.delete_entity(event.uuid)
    except Exception:
        error_counter.labels(event_type=event.event_type, entity=event.entity).inc()
        _logger.exception("Failed to process notification from master data: %s", event)


def _consume_master_data_notifications(redis: Redis) -> None:
    pubsub = redis.pubsub()
    pubsub.subscribe(Config.get_redis_channel())
    _logger.info("Redis channel subscribed")

    while True:
        message = pubsub.get_message(timeout=15)
        _logger.debug("Message received: %s", message)
        if _is_irrelevant(message):
            _logger.debug("Ignoring irrelevant message")
            continue
        event = _extract_event_details(message)
        if event is None:
            continue
        _logger.info("Event = %s", event)
        _process_event(event)


def subscribe_master_data_notifications() -> None:
    username, password = Config.get_redis_credentials()
    redis_client = Redis(
        host=Config.get_redis_host(),
        port=Config.get_redis_port(),
        username=username,
        password=password,
        charset="utf-8",
        decode_responses=True
    )
    _logger.info("Redis client created (consumer)")
    consumer_thread = Thread(
        name="Master-Data-Nofitication-Consumer",
        target=_consume_master_data_notifications,
        args=[redis_client],
        daemon=True
    )
    consumer_thread.start()
