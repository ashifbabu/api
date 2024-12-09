from pydantic import BaseModel
from typing import List, Optional

class Rule(BaseModel):
    paxType: Optional[str]
    cityPair: Optional[str]
    ruleType: Optional[str]
    ruleDetails: Optional[str]
    isRefundable: Optional[bool] = None
    refundableBeforeDeparture: Optional[float] = None
    refundableAfterDeparture: Optional[float] = None
    isExchangeable: Optional[bool] = None
    exchangeableBeforeDeparture: Optional[float] = None
    exchangeableAfterDeparture: Optional[float] = None

class RulesResponse(BaseModel):
    source: str
    rules: List[Rule]
    error: Optional[str]
