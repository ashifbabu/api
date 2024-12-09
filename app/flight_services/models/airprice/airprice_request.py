from pydantic import BaseModel, Field
from typing import List, Optional

class UnifiedAirPriceRequest(BaseModel):
    source: str = Field(..., example="bdfare", description="Data source: 'bdfare', 'flyhub', or 'all'")
    traceId: Optional[str] = Field(None, example="cd0cd824-c6bd-4025-893c-ccf4577dd454", description="Unique identifier for request tracking (used by both sources)")
    offerId: Optional[List[str]] = Field(None, example=["string"], description="List of offer IDs for BDFare or FlyHub")
    searchId: Optional[str] = Field(None, example="string", description="Search ID for FlyHub (mapped from traceId if applicable)")
    resultId: Optional[str] = Field(None, example="string", description="Result ID for FlyHub (mapped from first item in offerId if applicable)")
