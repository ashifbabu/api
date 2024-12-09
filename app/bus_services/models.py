from pydantic import BaseModel
from datetime import date

class BusSearchRequest(BaseModel):
    origin: str
    destination: str
    travel_date: date

