#app\flight_services\routes\combined\combined_search.py

from fastapi import APIRouter, Body, HTTPException
from app.flight_services.models.combined.combined_search import FlightSearchRequest
from app.flight_services.services.combined_service import combined_search
import logging

# Initialize the router and logger
router = APIRouter()
logger = logging.getLogger("combined_search")
logger.setLevel(logging.INFO)

# Configure logging (if not already configured globally)
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

@router.post("/search", tags=["Combined Search"])
async def search_flights(payload: FlightSearchRequest = Body(...)):
    """
    Perform a combined flight search based on the specified source.

    Args:
        payload (FlightSearchRequest): The flight search request payload.

    Returns:
        dict: Flight results from BDFare, FlyHub, or both.
    """
    try:
        logger.info("Received search request: %s", payload.dict())

        # Call the combined search service
        results = await combined_search(payload)

        logger.info("Search results successfully retrieved.")
        return results

    except ValueError as ve:
        logger.error("Validation error: %s", str(ve))
        raise HTTPException(status_code=422, detail=f"Validation Error: {str(ve)}")

    except HTTPException as he:
        logger.error("HTTP error: %s", he.detail)
        raise he

    except Exception as e:
        logger.exception("Unexpected error occurred during the flight search.")
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )



# #routes/combined/combined_search_results

# import asyncio
# from fastapi import APIRouter, HTTPException, Body
# from app.flight_services.clients.helpers import (
#     convert_bdfare_to_flyhub,
#     simplify_bdfare_response,
#     simplify_flyhub_response,
# )
# from app.flight_services.clients.fetchers import fetch_bdfare_flights, fetch_flyhub_flights
# from app.flight_services.models.combined.combined_search import RequestPayload

# router = APIRouter()

# @router.post("/search")
# async def combined_search(payload: RequestPayload):
#     """
#     Perform a flight search based on the specified source.
    
#     Args:
#         payload (RequestPayload): The flight search request payload.

#     Returns:
#         dict: Simplified flight results based on the source (bdfare, flyhub, or all).
#     """
#     # Extract the source parameter
#     source = payload.source.lower()

#     # Convert BDFare payload to FlyHub payload
#     flyhub_payload = convert_bdfare_to_flyhub(payload.dict())

#     try:
#         # Initialize tasks based on the source
#         tasks = {}
#         if source in ["bdfare", "all"]:
#             tasks["bdfare"] = fetch_bdfare_flights(payload.dict())
#         if source in ["flyhub", "all"]:
#             tasks["flyhub"] = fetch_flyhub_flights(flyhub_payload)

#         # Execute tasks concurrently if more than one source is selected
#         results = await asyncio.gather(*tasks.values(), return_exceptions=True)

#         # Simplify responses
#         simplified_results = {}
#         if "bdfare" in tasks:
#             bdfare_response = results[list(tasks.keys()).index("bdfare")]
#             if isinstance(bdfare_response, Exception):
#                 raise bdfare_response
#             simplified_results["bdfare"] = simplify_bdfare_response(bdfare_response)

#         if "flyhub" in tasks:
#             flyhub_response = results[list(tasks.keys()).index("flyhub")]
#             if isinstance(flyhub_response, Exception):
#                 raise flyhub_response
#             simplified_results["flyhub"] = simplify_flyhub_response(flyhub_response)

#         # Return results based on the source
#         if source == "bdfare":
#             return {"bdfare": simplified_results.get("bdfare")}
#         elif source == "flyhub":
#             return {"flyhub": simplified_results.get("flyhub")}
#         elif source == "all":
#             return simplified_results

#     except Exception as e:
#         # Handle exceptions
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



