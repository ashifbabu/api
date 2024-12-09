from pydantic import BaseModel
from typing import Optional, Dict

class BalanceResponse(BaseModel):
    Balance: float
    Credits: float
    Status: str
    Error: Optional[Dict[str, str]] = None
