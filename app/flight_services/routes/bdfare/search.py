from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import subprocess
import json
from dotenv import load_dotenv
import logging
import httpx

# Load .env file
load_dotenv()

# Initialize router
router = APIRouter()

# Load BDFare API details from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Pydantic models for request and response
class TravelPreferences(BaseModel):
    vendorPref: List[str] = Field(default=[])
    cabinCode: str = Field(default="Economy")


class OriginDepRequest(BaseModel):
    iatA_LocationCode: str = Field(example="JSR")
    date: str = Field(example="2024-12-15")


class DestArrivalRequest(BaseModel):
    iatA_LocationCode: str = Field(example="DAC")


class OriginDest(BaseModel):
    originDepRequest: OriginDepRequest
    destArrivalRequest: DestArrivalRequest


class Pax(BaseModel):
    paxID: str = Field(example="PAX1")
    ptc: str = Field(example="ADT")  # Passenger type code: ADT (adult), CHD (child), INF (infant)


class ShoppingCriteria(BaseModel):
    tripType: str = Field(default="Oneway", example="Oneway")
    travelPreferences: TravelPreferences
    returnUPSellInfo: bool = Field(default=True)


class AirShoppingRequest(BaseModel):
    pointOfSale: str = Field(default="BD", example="BD")
    request: Dict[str, Any] = Field(
        example={
            "originDest": [
                {
                    "originDepRequest": {
                        "iatA_LocationCode": "JSR",
                        "date": "2024-12-15"
                    },
                    "destArrivalRequest": {
                        "iatA_LocationCode": "DAC"
                    }
                }
            ],
            "pax": [
                {
                    "paxID": "PAX1",
                    "ptc": "ADT"
                }
            ],
            "shoppingCriteria": {
                "tripType": "Oneway",
                "travelPreferences": {
                    "vendorPref": [],
                    "cabinCode": "Economy"
                },
                "returnUPSellInfo": True
            }
        }
    )


class AirShoppingResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


@router.post(
    "/airshopping",
    response_model=AirShoppingResponse,
    summary="Search Flights",
    description="Search and retrieve flight results using the BDFare API.",
)
async def search_flights(payload: AirShoppingRequest):
    """
    Search and retrieve flight results using BDFare API with curl.

    Args:
        payload (AirShoppingRequest): The flight search request payload.

    Returns:
        AirShoppingResponse: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = [
        "Content-Type: application/json",
        f"X-API-KEY: {BDFARE_API_KEY}"
    ]

    # Convert payload to JSON string
    payload_json = json.dumps(payload.dict())

    # Construct the curl command
    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", headers[0],  # Content-Type
        "-H", headers[1],  # X-API-KEY
        "-d", payload_json  # Data payload
    ]

    logger.info(f"Executing curl command: {' '.join(curl_command)}")

    try:
        # Execute the curl command
        result = subprocess.run(curl_command, capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            logger.error(f"Curl command failed: {result.stderr}")
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )

        # Parse the response JSON
        response_data = json.loads(result.stdout)
        logger.debug(f"Curl Response: {response_data}")

        return AirShoppingResponse(success=True, data=response_data)

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from curl: {result.stdout}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to decode JSON response: {result.stdout}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error occurred using curl: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred using curl: {str(e)}"
        )
