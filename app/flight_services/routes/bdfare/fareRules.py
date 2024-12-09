from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
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
class FareRulesRequest(BaseModel):
    traceId: str = Field(..., example="ce30ea06-20c2-46b9-8084-5bcad3632d4b")
    offerId: str = Field(..., example="64f45d2a-86a8-4f6d-9a0f-38a632a108d3")


class FareRulesResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


@router.post(
    "/farerules",
    response_model=FareRulesResponse,
    summary="Retrieve Fare Rules",
    description="Fetch Fare Rules details using the BDFare API.",
)
async def get_fare_rules(payload: FareRulesRequest):
    """
    Fetch Fare Rules details using BDFare API, with a curl fallback.

    Args:
        payload (FareRulesRequest): The Fare Rules request payload.

    Returns:
        FareRulesResponse: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/FareRules"
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json",
    }

    logger.info(f"Making request to BDFare API: {url}")
    logger.debug(f"Payload: {payload.dict()}")

    # Attempt using httpx
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload.dict(), headers=headers)
        
        logger.info(f"BDFare API responded with status code: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            logger.debug(f"Response: {response_data}")
            return FareRulesResponse(success=True, data=response_data)
        else:
            logger.error(f"Error response from BDFare API: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"BDFare API error: {response.text}",
            )

    except httpx.RequestError as exc:
        logger.exception(f"Error communicating with BDFare API using httpx: {exc}")
        logger.info("Falling back to curl...")

        # Use curl as a fallback
        try:
            # Convert payload to JSON string for curl
            payload_json = json.dumps(payload.dict())

            # Construct the curl command
            curl_command = [
                "curl",
                "-X", "POST",
                url,
                "-H", f"X-API-KEY: {BDFARE_API_KEY}",
                "-H", "Content-Type: application/json",
                "-d", payload_json
            ]

            # Execute the curl command
            result = subprocess.run(curl_command, capture_output=True, text=True)

            # Check for errors
            if result.returncode != 0:
                logger.error(f"Curl command failed: {result.stderr}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Curl command failed: {result.stderr}"
                )

            # Parse and return the JSON response
            response_json = json.loads(result.stdout)
            logger.debug(f"Curl Response: {response_json}")
            return FareRulesResponse(success=True, data=response_json)

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
