from pydantic import BaseModel, Field
from typing import List


class FlyHubSegmentRequest(BaseModel):
    Origin: str = Field(..., example="JSR")
    Destination: str = Field(..., example="DAC")
    CabinClass: str = Field(..., example="Economy")
    DepartureDateTime: str = Field(..., example="2024-12-15T00:00:00")


class FlyHubRequest(BaseModel):
    AdultQuantity: int = Field(..., example=1)
    ChildQuantity: int = Field(..., example=0)
    InfantQuantity: int = Field(..., example=0)
    JourneyType: str = Field(..., example="1", description="1=One-way, 2=Return")
    Segments: List[FlyHubSegmentRequest]
