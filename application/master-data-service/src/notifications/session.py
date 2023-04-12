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
from typing import Type

from redis import ConnectionPool, Redis

from config import Config

from .dto import Event, EventType


_logger = getLogger("notifications")


_pool = ConnectionPool(
    host=Config.get_redis_host(),
    port=Config.get_redis_port(),
    db=0,
    decode_responses=True,
    max_connections=10
)
_logger.info("Redis connection pool created (host = %s, port = %d)", Config.get_redis_host(), Config.get_redis_port())


class Notifier:

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    def send_notification(self, event_type: EventType, entity: Type, uuid: str) -> None:
        event = Event(
            event_type=event_type,
            entity=entity,
            uuid=uuid
        )
        self._redis.publish(Config.get_redis_channel(), event.json())
        _logger.debug("Notification sent - event = %s, entity = %s, uuid = %s", event_type, entity, uuid)


def get_notifier() -> Notifier:
    redis = Redis(connection_pool=_pool)
    try:
        _logger.debug("Redis session created")
        yield Notifier(redis)
    finally:
        redis.close()
        _logger.debug("Redis session closed")
