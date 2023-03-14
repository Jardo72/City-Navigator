FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY *.py ./

RUN pip install --no-cache-dir -r requirements.txt

USER 1000:1000

EXPOSE 8000

CMD [ "uvicorn", "main:app" ]
