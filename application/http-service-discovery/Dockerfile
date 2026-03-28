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

FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY src ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvloop
RUN rm requirements.txt

USER 1000:1000

EXPOSE 8000

ENV ACCESS_LOG=${ACCESS_LOG:-/proc/1/fd/1}
ENV LOG_CONFIG=/usr/src/app/logging.ini

ENTRYPOINT /usr/local/bin/gunicorn \
    -b 0.0.0.0:8000 \
    -w 1 \
    -k uvicorn.workers.UvicornWorker main:app \
    --log-config ${LOG_CONFIG} \
    --access-logfile ${ACCESS_LOG}
