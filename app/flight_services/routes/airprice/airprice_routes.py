from fastapi import APIRouter, HTTPException, Body
from app.flight_services.models.airprice.airprice_request import UnifiedAirPriceRequest
from app.flight_services.services.airprice_service import fetch_airprice
import logging

router = APIRouter()
logger = logging.getLogger("airprice_routes")

@router.post("/price", tags=["AirPrice"])
async def get_airprice(payload: UnifiedAirPriceRequest = Body(...)):
    """
    Fetch air pricing details based on the unified request format.

    Args:
        payload (UnifiedAirPriceRequest): Unified request payload.

    Returns:
        dict: Unified air pricing details.
    """
    try:
        logger.info(f"Received request: {payload.dict()}")
        response = await fetch_airprice(payload)
        logger.info(f"Returning response: {response}")
        return response
    except HTTPException as he:
        logger.error(f"HTTPException occurred: {he.detail}")
        raise he
    except Exception as e:
        logger.exception("Unexpected error occurred while fetching air pricing.")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")