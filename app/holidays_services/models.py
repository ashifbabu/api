from pydantic import BaseModel
from datetime import date

class HolidaySearchRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget: float
