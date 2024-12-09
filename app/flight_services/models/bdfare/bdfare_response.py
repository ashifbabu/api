from pydantic import BaseModel, Field
from typing import List


class BDFarePriceDetails(BaseModel):
    baseFare: float = Field(..., example=4274.0)
    tax: float = Field(..., example=975.0)
    discount: float = Field(..., example=0.0)
    total: float = Field(..., example=5249.0)
    currency: str = Field(..., example="BDT")


class BDFareSegmentResponse(BaseModel):
    from_: str = Field(..., alias="from", example="JSR")
    to: str = Field(..., example="DAC")
    departureTime: str = Field(..., example="2024-12-15T09:00:00Z")
    arrivalTime: str = Field(..., example="2024-12-15T09:45:00Z")
    airlineCode: str = Field(..., example="BS")
    flightNumber: str = Field(..., example="122")


class BDFareOffer(BaseModel):
    offerId: str = Field(..., example="05566b88-55b7-41f5-bda0-6ed2cff67f55")
    validatingCarrier: str = Field(..., example="BS")
    refundable: bool = Field(..., example=True)
    fareType: str = Field(..., example="OnHold")
    price: BDFarePriceDetails
    segments: List[BDFareSegmentResponse]
    seatsRemaining: int = Field(..., example=9)
