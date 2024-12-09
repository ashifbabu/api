from pydantic import BaseModel, Field
from typing import List


class FlyHubPriceDetails(BaseModel):
    BaseFare: float = Field(..., example=3524.0)
    Tax: float = Field(..., example=975.0)
    Discount: float = Field(..., example=280.0)
    Total: float = Field(..., example=4219.0)
    Currency: str = Field(..., example="BDT")


class FlyHubSegmentResponse(BaseModel):
    Origin: dict = Field(..., example={"Airport": {"AirportCode": "JSR", "AirportName": "Jessore Airport"}})
    Destination: dict = Field(..., example={"Airport": {"AirportCode": "DAC", "AirportName": "Dhaka Airport"}})
    DepTime: str = Field(..., example="2024-12-15T17:15:00")
    ArrTime: str = Field(..., example="2024-12-15T18:00:00")
    Airline: dict = Field(..., example={"AirlineCode": "BG", "FlightNumber": "468", "CabinClass": "Economy"})


class FlyHubOffer(BaseModel):
    ResultID: str = Field(..., example="347223ac-354b-45ba-baa9-b264ba98c5a5")
    Validatingcarrier: str = Field(..., example="BG")
    IsRefundable: bool = Field(..., example=True)
    FareType: str = Field(..., example="NET")
    Fares: List[FlyHubPriceDetails]
    Segments: List[FlyHubSegmentResponse]
    Availabilty: int = Field(..., example=9)
