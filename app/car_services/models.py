from pydantic import BaseModel

class CarSearchRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    pickup_date: str
    dropoff_date: str
