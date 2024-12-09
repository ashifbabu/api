from app.flight_services.clients.bdfare_client import fetch_bdfare_airprice
from app.flight_services.clients.flyhub_client import fetch_flyhub_airprice
from app.flight_services.adapters.airprice_adapter_bdfare import adapt_bdfare_response
from app.flight_services.adapters.airprice_adapter_flyhub import convert_bdfare_to_flyhub_airprice_request
import logging
from fastapi import HTTPException

logger = logging.getLogger("airprice_service")

async def fetch_airprice(payload):
    """
    Fetch air pricing details from BDFare or FlyHub.
    """
    source = payload.source.lower()

    if source == "bdfare":
        raw_response = await fetch_bdfare_airprice(payload.traceId, payload.offerId)
        return raw_response  # Return raw response directly

    elif source == "flyhub":
        logger.info("Processing request for FlyHub.")
        flyhub_payload = convert_bdfare_to_flyhub_airprice_request(payload.dict())
        raw_response = await fetch_flyhub_airprice(flyhub_payload["SearchID"], flyhub_payload["ResultID"])
        return raw_response  # Return raw response directly

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported source: {source}")
