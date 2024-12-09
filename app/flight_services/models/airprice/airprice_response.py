from pydantic import BaseModel, Field
from typing import List, Optional

class AirPriceSegment(BaseModel):
    from_: str = Field(..., alias="from", example="DAC")
    to: str = Field(..., example="DXB")
    departureTime: str = Field(..., example="2024-12-06T02:54:17.481Z")
    arrivalTime: str = Field(..., example="2024-12-06T05:54:17.481Z")
    airline: str = Field(..., example="BS", description="Airline code")
    flightNumber: str = Field(..., example="123", description="Flight number")
    cabinClass: str = Field(..., example="Economy")
    durationMinutes: int = Field(..., example=120)

class AirPriceDetails(BaseModel):
    totalFare: float = Field(..., example=12000.0)
    currency: str = Field(..., example="BDT")
    refundable: bool = Field(..., example=True)
    segments: List[AirPriceSegment]

class AirPriceResponse(BaseModel):
    traceId: str = Field(..., example="cd0cd824-c6bd-4025-893c-ccf4577dd454")
    prices: List[AirPriceDetails]
