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

from socket import gethostname

from pythonjsonlogger.json import JsonFormatter as _JsonFormatter


_HOSTNAME = gethostname()


class JsonFormatter(_JsonFormatter):

    def __init__(self, fmt=None, datefmt=None, style="%", validate=True, **kwargs):
        super().__init__(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        )

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["instance"] = _HOSTNAME
        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_record["exception"] = {
                "class": exc_type.__name__,
                "message": str(exc_value),
                "traceback": self.formatException(record.exc_info),
            }
            record.exc_info = None
            record.exc_text = None
