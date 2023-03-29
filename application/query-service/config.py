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

from os import environ


class Config:

    @staticmethod
    def get_master_data_service_base_url() -> str:
        return Config._get_environment_variable("MASTER_DATA_SERVICE_BASE_URL", "http://localhost:90")

    @staticmethod
    def get_database_url() -> str:
        return Config._get_environment_variable("DATABASE_URL", "sqlite://")

    @staticmethod
    def _get_environment_variable(name: str, default_value: str) -> str:
        result = environ[name]
        if result is None:
            result = default_value
        return result
