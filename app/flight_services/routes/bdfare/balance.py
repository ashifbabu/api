from fastapi import APIRouter, HTTPException
from app.flight_services.clients.bdfare_client import BDFAREClient

router = APIRouter()

@router.get("/balance", tags=["Flights"])
async def get_bdfare_balance():
    try:
        client = BDFAREClient()
        balance = client.get_balance()
        return balance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
