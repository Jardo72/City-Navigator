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

from config import Config

from redis import ConnectionPool, Redis


_pool = ConnectionPool(
    host=Config.get_redis_host(),
    port=Config.get_redis_port(),
    db=0,
    decode_responses=True
)


def get_redis() -> Redis:
    redis = Redis(connection_pool=_pool)
    try:
        yield redis
    finally:
        redis.close()

# TODO: remove when not needed anymore
# see https://stackoverflow.com/questions/73563804/what-is-the-recommended-way-to-instantiate-and-pass-around-a-redis-client-with-f
