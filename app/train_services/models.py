from pydantic import BaseModel
from datetime import date

class TrainSearchRequest(BaseModel):
    origin: str
    destination: str
    travel_date: date
