#
# Copyright 2026 Jaroslav Chmurny
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
from typing import Optional, Tuple


_logger = getLogger("config")


class UndefinedMandatoryEnvironmentVariableError(Exception):
    def __init__(self, variable_name: str) -> None:
        super().__init__(f"Mandatory environment variable '{variable_name}' is not defined")


class IncompleteRedisCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__("Incomplete Redis credentials: either both REDIS_USERNAME and REDIS_PASSWORD must be defined, or neither of them")


class BaseConfig:

    @staticmethod
    @cache
    def is_api_doc_enabled() -> bool:
        value = BaseConfig._get_mandatory_env_var("API_DOC_ENABLED", default_value="NO")
        return value.upper() in {"YES", "TRUE", "1"}

    @staticmethod
    @cache
    def get_root_path() -> str:
        return BaseConfig._get_mandatory_env_var("ROOT_PATH", default_value="")

    @staticmethod
    @cache
    def get_redis_host() -> str:
        return BaseConfig._get_mandatory_env_var("REDIS_HOST")

    @staticmethod
    @cache
    def get_redis_port() -> int:
        value = BaseConfig._get_mandatory_env_var("REDIS_PORT", default_value="6379")
        return int(value)

    @staticmethod
    @cache
    def get_redis_credentials() -> Tuple[Optional[str], Optional[str]]:
        username = BaseConfig._get_optional_env_var("REDIS_USERNAME")
        password = BaseConfig._get_optional_env_var("REDIS_PASSWORD")
        if (username is None) != (password is None):
            raise IncompleteRedisCredentialsError()
        return username, password

    @staticmethod
    @cache
    def get_redis_channel() -> str:
        return BaseConfig._get_mandatory_env_var("REDIS_CHANNEL", default_value="city-navigator")

    @staticmethod
    @cache
    def get_app_port() -> int:
        value = BaseConfig._get_mandatory_env_var("APP_PORT", default_value="8000")
        return int(value)

    @staticmethod
    @cache
    def get_prometheus_discovery_base_url() -> Optional[str]:
        return BaseConfig._get_optional_env_var("PROMETHEUS_DISCOVERY_BASE_URL")

    @staticmethod
    @cache
    def get_heartbeat_interval_seconds() -> int:
        value = BaseConfig._get_mandatory_env_var("HEARTBEAT_INTERVAL_SECONDS", default_value="15")
        return int(value)

    @staticmethod
    def _get_mandatory_env_var(name: str, default_value: Optional[str] = None) -> str:
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

    @staticmethod
    def _get_optional_env_var(name: str) -> Optional[str]:
        result = environ.get(name, None)
        _logger.info("Config - env. var = '%s', defined = %s", name, result is not None)
        return result
