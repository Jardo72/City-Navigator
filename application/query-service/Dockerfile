FROM python:3.11-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY logging.ini ./
COPY src ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvloop
RUN rm requirements.txt

ENV PROMETHEUS_MULTIPROC_DIR=/prometheus/multiproc
RUN mkdir -p ${PROMETHEUS_MULTIPROC_DIR}
RUN chown -R 1000:1000 ${PROMETHEUS_MULTIPROC_DIR}
RUN chmod -R u+rwx ${PROMETHEUS_MULTIPROC_DIR}

USER 1000:1000

EXPOSE 8000

ENTRYPOINT /usr/local/bin/gunicorn \
    -b 0.0.0.0:8000 \
    -w 6 \
    -k uvicorn.workers.UvicornWorker main:app \
    --log-config logging.ini
