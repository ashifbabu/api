import httpx
import os
import logging
import time  # Import the time module
from dotenv import load_dotenv  # Import dotenv
from fastapi import HTTPException
from app.flight_services.clients.flyhub_client import get_flyhub_token

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")

# Validate environment variables
if not BDFARE_BASE_URL or not BDFARE_API_KEY or not FLYHUB_BASE_URL:
    logger.error("Missing required environment variables for BDFare or FlyHub.")
    raise ValueError("Missing required environment variables for BDFare or FlyHub.")

logger.info("Environment variables loaded successfully.")

# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}

def transform_to_bdfare_request(data: dict) -> dict:
    """
    Transform the input data to match the BDFare request format.

    Args:
        data (dict): The original request data.

    Returns:
        dict: Transformed data in BDFare format.
    """
    # Ensure required fields are available or transform the data as needed
    transformed_data = {
        "SearchId": data.get("SearchId"),
        "ResultId": data.get("ResultId"),
        "OfferId": data.get("OfferId"),  # Assuming OfferId is also provided in the input
        "TraceId": data.get("TraceId")   # Assuming TraceId is also provided in the input
    }

    # Check if any required field is missing and handle accordingly
    if not transformed_data["OfferId"] or not transformed_data["TraceId"]:
        raise ValueError("OfferId and TraceId are required for BDFare request.")

    return transformed_data

async def fetch_bdfare_rules(endpoint: str, payload: dict):
    """
    Fetch rules from the BDFare API.

    Args:
        endpoint (str): The endpoint to call (e.g., "MiniRule" or "FareRules").
        payload (dict): The request payload.

    Returns:
        dict: The response from the BDFare API.
    """
    url = f"{BDFARE_BASE_URL.rstrip('/')}/{endpoint}"  # Ensure no trailing slashes
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    try:
        logger.info(f"Sending request to BDFare API at {url} with payload: {payload}")
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"BDFare API response: {response.json()}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"BDFare API returned error: {e.response.status_code} {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"BDFare API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while calling BDFare API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while calling BDFare API: {str(e)}"
        )


async def fetch_flyhub_rules(endpoint: str, payload: dict):
    """
    Fetch rules from the FlyHub API.

    Args:
        endpoint (str): The endpoint to call (e.g., "AirMiniRules" or "AirRules").
        payload (dict): The request payload.

    Returns:
        dict: The response from the FlyHub API.
    """
    # Ensure we have a valid token
    global cached_token
    if not cached_token["token"] or cached_token["expires_at"] <= time.time():
        logger.info("Fetching new FlyHub token...")
        cached_token["token"] = get_flyhub_token()  # Call the function to get a new token
        cached_token["expires_at"] = time.time() + 3600  # Set the new expiration time

    url = f"{FLYHUB_BASE_URL.rstrip('/')}/{endpoint}"  # Ensure no trailing slashes
    headers = {"Authorization": f"Bearer {cached_token['token']}", "Content-Type": "application/json"}

    try:
        logger.info(f"Sending request to FlyHub API at {url} with payload: {payload}")
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info(f"FlyHub API response: {response.json()}")
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"FlyHub API returned error: {e.response.status_code} {e.response.text}")
        if e.response.status_code == 401:  # Token expired or invalid
            logger.info("FlyHub token expired. Fetching a new token...")
            cached_token["token"] = get_flyhub_token()
            cached_token["expires_at"] = time.time() + 3600  # Update token expiration
            headers["Authorization"] = f"Bearer {cached_token['token']}"
            # Retry the request
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                logger.info(f"FlyHub API response after retry: {response.json()}")
                return response.json()
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"FlyHub API error: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Unexpected error while calling FlyHub API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while calling FlyHub API: {str(e)}"
        )
