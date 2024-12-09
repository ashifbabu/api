# from fastapi import APIRouter, HTTPException
# from app.flight_services.clients.flyhub_client import FlyhubClient

# router = APIRouter()

# @router.get("/balance", tags=["Flights"])
# async def get_flyhub_balance():
#     try:
#         client = FlyhubClient()
#         balance = client.get_balance()
#         return balance
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
