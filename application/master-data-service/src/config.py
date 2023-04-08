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
from os import environ


_logger = getLogger("config")


class Config:

    @staticmethod
    def get_database_url() -> str:
        return Config._get_environment_variable(
            name="DATABASE_URL",
            default_value=None
        )

    @staticmethod
    def get_redis_host() -> str:
        return Config._get_environment_variable(
            name="REDIS_HOST",
            default_value="localhost"
        )

    @staticmethod
    def get_redis_port() -> int:
        value = Config._get_environment_variable(
            name="REDIS_PORT",
            default_value="6379"
        )
        return int(value)

    @staticmethod
    def _get_environment_variable(name: str, default_value: str) -> str:
        result = environ.get(name, None)
        default_used = False
        if result is None:
            default_used = True
            result = default_value
        _logger.info("Config - env. var = '%s', result = '%s', default used = %s", name, result, default_used)
        return result
