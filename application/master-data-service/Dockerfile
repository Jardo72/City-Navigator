FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY *.py ./

# TODO: temporary hack - remove
COPY test.db ./

RUN pip install --no-cache-dir -r requirements.txt

USER 1000:1000

EXPOSE 8000

# TODO: see
# - https://youtu.be/qQNGw_m8t0Y?t=2073
# - https://youtu.be/qQNGw_m8t0Y?t=2999

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]
