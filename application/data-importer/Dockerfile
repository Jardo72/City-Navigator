FROM python:3.11-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY city-plan.json ./
COPY src ./

RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

USER 1000:1000

ENTRYPOINT [ "python", "main.py" ]
# TODO
CMD [] 
