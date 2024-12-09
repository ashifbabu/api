from pydantic import BaseModel
from typing import Optional

class RulesRequest(BaseModel):
    source: str  # "bdfare" or "flyhub"
    rule_type: str  # "fare" or "mini"
    data: dict  # Request payload for the specific API
