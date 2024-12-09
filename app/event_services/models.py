from pydantic import BaseModel
from datetime import date

class EventSearchRequest(BaseModel):
    location: str
    event_date: date
    category: str
