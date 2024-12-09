#app\flight_services\models\combined\combined_search.py
from pydantic import BaseModel, Field
from typing import List, Optional


class PriceDetails(BaseModel):
    baseFare: float = Field(..., example=200.0)
    tax: float = Field(..., example=50.0)
    discount: float = Field(..., example=10.0)
    total: float = Field(..., example=240.0)
    currency: str = Field(..., example="USD")


class FlightSegment(BaseModel):
    from_: str = Field(..., alias="from")
    fromAirportName: Optional[str]
    to: str
    toAirportName: Optional[str]
    departureTime: str
    arrivalTime: str
    airlineCode: str
    airlineName: Optional[str]
    flightNumber: str
    cabinClass: str
    durationMinutes: str

class BaggageDetails(BaseModel):
    from_: str = Field(..., alias="from", example="JFK")
    to: str = Field(..., example="LAX")
    checkIn: Optional[List[dict]] = Field(None, example=[{"paxType": "ADT", "allowance": "20kg"}])
    cabin: Optional[List[dict]] = Field(None, example=[{"paxType": "ADT", "allowance": "7kg"}])


class FlightSearchResponse(BaseModel):
    id: str = Field(..., example="12345")
    airline: str = Field(..., example="AA")
    airlineName: Optional[str] = Field(None, example="American Airlines")
    refundable: bool = Field(..., example=True)
    fareType: str = Field(..., example="OnHold")
    price: PriceDetails
    segments: List[FlightSegment]
    baggageAllowance: List[BaggageDetails]
    seatsRemaining: int = Field(..., example=9)


class FlightSearchRequest(BaseModel):
    pointOfSale: str = Field(..., example="BD")
    source: str = Field(..., example="all", description="Specify data source: 'bdfare', 'flyhub', or 'all'")
    request: dict  # This can be further broken into nested models for validation.



# from pydantic import BaseModel, Field
# from typing import List, Optional, Dict

# class TravelPreferences(BaseModel):
#     vendorPref: List[str] = Field(default=[], example=[])
#     cabinCode: str = Field(..., example="Economy")

# class ShoppingCriteria(BaseModel):
#     tripType: str = Field(..., example="Oneway")
#     travelPreferences: TravelPreferences
#     returnUPSellInfo: Optional[bool] = Field(default=True, example=True)

# class OriginDepRequest(BaseModel):
#     iatA_LocationCode: str = Field(..., example="JSR")
#     date: str = Field(..., example="2024-12-15")

# class DestArrivalRequest(BaseModel):
#     iatA_LocationCode: str = Field(..., example="DAC")

# class OriginDest(BaseModel):
#     originDepRequest: OriginDepRequest
#     destArrivalRequest: DestArrivalRequest

# class Pax(BaseModel):
#     paxID: str = Field(..., example="PAX1")
#     ptc: str = Field(..., example="ADT")  # Passenger Type Code

# class Request(BaseModel):
#     originDest: List[OriginDest]
#     pax: List[Pax]
#     shoppingCriteria: ShoppingCriteria

# class RequestPayload(BaseModel):
#     pointOfSale: str = Field(..., example="BD")
#     source: str = Field(..., example="all", description="Specify data source: 'bdfare', 'flyhub', or 'all'")
#     request: Request
