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

from functools import cache
from logging import getLogger
from os import environ
from typing import Optional


_logger = getLogger("config")


class UndefinedMandatoryEnvironmentVariableError(Exception):
    def __init__(self, variable_name: str) -> None:
        super().__init__(f"Mandatory environment variable '{variable_name}' is not defined")


class Config:

    @staticmethod
    def is_api_doc_enabled() -> bool:
        value = Config._get_environment_variable("API_DOC_ENABLED", default_value="NO")
        return value.upper() in {"YES", "TRUE", "1"}

    @staticmethod
    def get_root_path() -> str:
        return Config._get_environment_variable("ROOT_PATH", default_value="")

    @staticmethod
    def get_database_url() -> str:
        return Config._get_environment_variable("DATABASE_URL")

    @staticmethod
    def get_redis_host() -> str:
        return Config._get_environment_variable("REDIS_HOST")

    @staticmethod
    def get_redis_port() -> int:
        value = Config._get_environment_variable("REDIS_PORT", default_value="6379")
        return int(value)

    @staticmethod
    def get_redis_channel() -> str:
        return Config._get_environment_variable("REDIS_CHANNEL", default_value="city-navigator")

    @staticmethod
    def get_app_port() -> int:
        value = Config._get_environment_variable("APP_PORT", default_value="8000")
        return int(value)

    @staticmethod
    def get_prometheus_discovery_base_url() -> str:
        return Config._get_environment_variable("PROMETHEUS_DISCOVERY_BASE_URL")

    @staticmethod
    def get_heartbeat_interval_seconds() -> int:
        value = Config._get_environment_variable("HEARTBEAT_INTERVAL_SECONDS", default_value="15")
        return int(value)

    @staticmethod
    @cache
    def _get_environment_variable(name: str, default_value: Optional[str] = None) -> str:
        result = environ.get(name, None)
        default_used = False
        if result is None and default_value is None:
            _logger.error("Mandatory environment variable '%s' is not defined and no default value is provided", name)
            raise UndefinedMandatoryEnvironmentVariableError(name)
        if result is None:
            default_used = True
            result = default_value
        _logger.info("Config - env. var = '%s', result = '%s', default used = %s", name, result, default_used)
        return result
