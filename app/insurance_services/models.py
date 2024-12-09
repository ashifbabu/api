from pydantic import BaseModel
from datetime import date

class InsuranceRequest(BaseModel):
    coverage_type: str
    travel_start: date
    travel_end: date
    traveler_count: int
