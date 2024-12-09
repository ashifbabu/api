from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
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
class Phone(BaseModel):
    phoneNumber: str = Field(..., example="1234567")
    countryDialingCode: str = Field(..., example="880")


class ContactInfo(BaseModel):
    phone: Phone
    emailAddress: str = Field(..., example="abc@xyz.com")


class IdentityDoc(BaseModel):
    identityDocType: str = Field(..., example="Passport")
    identityDocID: str = Field(..., example="BB458924")
    expiryDate: str = Field(..., example="2025-12-27")


class Individual(BaseModel):
    givenName: str = Field(..., example="John")
    surname: str = Field(..., example="Wick")
    gender: str = Field(..., example="Male")
    birthdate: str = Field(..., example="1978-12-25")
    nationality: str = Field(..., example="BD")
    identityDoc: IdentityDoc


class PaxList(BaseModel):
    ptc: str = Field(..., example="Adult")
    individual: Individual


class OrderSellRequestPayload(BaseModel):
    contactInfo: ContactInfo
    paxList: List[PaxList]


class OrderSellRequest(BaseModel):
    traceId: str = Field(..., example="ce30ea06-20c2-46b9-8084-5bcad3632d4b")
    offerId: List[str] = Field(..., example=["64f45d2a-86a8-4f6d-9a0f-38a632a108d3"])
    request: OrderSellRequestPayload


class OrderSellResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


@router.post(
    "/airprebook",
    response_model=OrderSellResponse,
    summary="Place Order Sell",
    description="Create and confirm an order sell using the BDFare API.",
)
async def place_order_sell(payload: OrderSellRequest):
    """
    Create and confirm an order sell using BDFare API with curl.

    Args:
        payload (OrderSellRequest): The order sell request payload.

    Returns:
        OrderSellResponse: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/OrderSell"

    # Convert payload to JSON string for curl
    payload_json = json.dumps(payload.dict())

    # Construct the curl command
    curl_command = [
        "curl",
        "-X", "POST",
        url,
        "-H", f"X-API-KEY: {BDFARE_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload_json,
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

        return OrderSellResponse(success=True, data=response_data)

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
