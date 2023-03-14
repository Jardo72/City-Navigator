from typing import List, Optional
from pydantic import BaseModel


class CreateMeansOfTransportRequest(BaseModel):
    identifier: str = None
