from pydantic import BaseModel, Field
from typing import List, Literal


class OriginDepRequest(BaseModel):
    iatA_LocationCode: str = Field(..., example="JSR")
    date: str = Field(..., example="2024-12-15")


class DestArrivalRequest(BaseModel):
    iatA_LocationCode: str = Field(..., example="DAC")


class BDFareSegmentRequest(BaseModel):
    originDepRequest: OriginDepRequest
    destArrivalRequest: DestArrivalRequest


class PaxRequest(BaseModel):
    paxID: str = Field(..., example="PAX1")
    ptc: Literal["ADT", "CHD", "INF"] = Field(..., example="ADT")


class TravelPreferences(BaseModel):
    vendorPref: List[str] = Field(..., example=[])
    cabinCode: Literal["Economy", "Business", "First"] = Field(..., example="Economy")


class ShoppingCriteria(BaseModel):
    tripType: Literal["Oneway", "Return", "Multicity"] = Field(..., example="Oneway")
    travelPreferences: TravelPreferences
    returnUPSellInfo: bool = Field(..., example=True)


class RequestPayload(BaseModel):
    originDest: List[BDFareSegmentRequest]
    pax: List[PaxRequest]
    shoppingCriteria: ShoppingCriteria


class CombinedSearchInput(BaseModel):
    pointOfSale: str = Field(..., example="BD")
    source: Literal["all", "bdfare", "flyhub"] = Field(..., example="all")
    request: RequestPayload
