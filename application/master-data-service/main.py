from typing import List

from fastapi import FastAPI

from model import CreateMeansOfTransportRequest


app = FastAPI()


@app.get("/means-of-transport", response_model=List[])
async def get_means_of_transport_list():
    ...


@app.get("/means-of-transport/{uuid}")
async def get_means_of_transport(uuid: str):
    ...


@app.post("/means-of-transport/", status_code=201)
async def create_means_of_transport(request: CreateMeansOfTransportRequest):
    ...


@app.put("/means-of-transport/{uuid}")
async def update_means_of_transport(request: CreateMeansOfTransportRequest):
    ...


@app.delete("/means-of-transport/{uuid}")
async def delete_means_of_transport(uuid: str):
    ...


@app.get("")
async def get_node():
    ...
