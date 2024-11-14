from pydantic import BaseModel
from datetime import date

class HotelSearchRequest(BaseModel):
    location: str
    check_in: date
    check_out: date
    guests: int

