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

from redis import Redis

from config import Config

from .dto import Entity, Event, EventType


_logger = getLogger("notifications")


def _is_irrelevant(message: Dict[str, Any]) -> bool:
    if message is None:
        return True
    if message["type"] != "message":
        return True
    if message["channel"] != Config.get_redis_channel():
        return True
    return False


def _extract_event_details(message: Dict[str, Any]) -> Event:
    try:
        json_data = loads(message["data"])
        event_type = json_data["event_type"]
        entity = json_data["entity"]
        uuid = json_data["uuid"]
        return Event(
            event_type=EventType[event_type.upper()],
            entity=Entity[entity.upper()],
            uuid=uuid
        )
    except Exception as e:
        _logger.error("Failed to extract event details from %s", message)
        _logger.error(str(e))
        return None


def _consume_master_data_notifications(redis: Redis) -> None:
    pubsub = redis.pubsub()
    pubsub.subscribe(Config.get_redis_channel())
    _logger.info("Redis channel subscribed")

    while True:
        message = pubsub.get_message(timeout=15)
        _logger.info("Message received: %s", message)
        if _is_irrelevant(message):
            _logger.debug("Ignoring irrelevant message")
            continue
        event = _extract_event_details(message)
        _logger.debug("Event = %s", event)
        if event is None:
            continue
        if event.entity == Entity.MEANS_OF_TRANSPORT:
            ...
        elif event.entity == Entity.STATION:
            ...
        elif event.entity == Entity.LINE:
            ...


def subscribe_master_data_notifications() -> None:
    redis_client = Redis(
        host=Config.get_redis_host(),
        port=Config.get_redis_port(),
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
