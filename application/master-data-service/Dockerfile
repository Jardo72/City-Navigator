FROM python:3.11-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY logging.ini ./
COPY src ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvloop
RUN rm requirements.txt

USER 1000:1000

EXPOSE 8000

ENTRYPOINT /usr/local/bin/gunicorn \
    -b 0.0.0.0:8000 \
    -w 4 \
    -k uvicorn.workers.UvicornWorker main:app \
    --log-config logging.ini
