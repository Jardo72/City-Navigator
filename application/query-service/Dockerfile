FROM python:3.11-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY logging.ini ./
COPY src ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvloop

USER 1000:1000

EXPOSE 8000

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-config", "logging.ini" ]
