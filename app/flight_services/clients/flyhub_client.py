#app\flight_services\clients\flyhub_client.py
import httpx
import json
import subprocess
from typing import Dict
from fastapi import HTTPException
import os
import logging
import time
from dotenv import load_dotenv  # Import dotenv

# Load environment variables from .env file
load_dotenv()

# Load API credentials from environment variables
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Logger setup
logger = logging.getLogger("flyhub_client")
logger.setLevel(logging.INFO)

# Example usage
if not FLYHUB_BASE_URL or not FLYHUB_USERNAME or not FLYHUB_API_KEY:
    logger.error("Missing required environment variables for FlyHub API.")
else:
    logger.info("FlyHub environment variables loaded successfully.")


# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


def validate_url(url: str):
    """Validate the FlyHub Base URL to ensure it includes a valid protocol."""
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=500,
            detail=f"Invalid FlyHub Base URL: {url}. Ensure it starts with 'http://' or 'https://'.",
        )


def get_flyhub_token() -> str:
    """
    Retrieve a valid token for FlyHub API.
    """
    global cached_token

    # Validate the FlyHub Base URL
    validate_url(FLYHUB_BASE_URL)

    # Check if the cached token is still valid
    if cached_token["token"] and cached_token["expires_at"] > time.time():
        return cached_token["token"]

    # Request a new token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        response = httpx.post(url, json=payload)
        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour (3600 seconds)
            cached_token["expires_at"] = time.time() + 3600
            logger.info("FlyHub token retrieved successfully.")
            return cached_token["token"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub Authentication Failed: {response.text}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during FlyHub Authentication: {str(e)}",
        )
#updated
async def fetch_flyhub_airprice(search_id: str, result_id: str):
    """
    Fetch air pricing details from FlyHub API.
    
    Args:
        search_id (str): The FlyHub search ID.
        result_id (str): The FlyHub result ID.
    
    Returns:
        dict: The response from the FlyHub API.
    
    Raises:
        HTTPException: If the request fails or an error occurs.
    """
    try:
        # Get a valid token (from cache or authenticate)
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500,
                detail="FlyHub authentication failed. Token is None."
            )
        
        # Set up the API endpoint and headers
        url = f"{FLYHUB_BASE_URL}/AirPrice"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        # Create the payload
        payload = {
            "SearchID": search_id,
            "ResultID": result_id,
        }
        
        # Log the request
        logger.info(f"Sending AirPrice request to FlyHub. URL: {url}")
        logger.info(f"Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
        
        # Raise for status if response indicates an error
        response.raise_for_status()
        
        # Log the response
        logger.info(f"FlyHub AirPrice response: {response.json()}")
        return response.json()

    except httpx.HTTPStatusError as http_err:
        logger.error(f"FlyHub API returned an HTTP error: {http_err.response.text}")
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"FlyHub API Error: {http_err.response.text}"
        )

    except Exception as e:
        logger.exception(f"Unexpected error occurred while fetching FlyHub AirPrice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching FlyHub AirPrice: {str(e)}"
        )

async def fetch_flyhub_flights(payload: dict) -> dict:
    """
    Fetch flights from FlyHub API with a fallback to curl.
    """
    try:
        # Authenticate and get the token
        token = get_flyhub_token()
        if not token:
            raise HTTPException(
                status_code=500, detail="FlyHub authentication failed. Token is None."
            )

        # Validate FlyHub Base URL
        validate_url(FLYHUB_BASE_URL)

        # FlyHub API endpoint
        url = f"{FLYHUB_BASE_URL}/AirSearch"

        # Headers with the token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        # Log the request payload
        logger.info(f"Sending request to FlyHub: {url}")
        logger.info(f"Headers: {headers}")
        logger.info(f"Payload: {payload}")

        # Attempt to fetch data using httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info("FlyHub response received successfully.")
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub API Error: {response.text}",
            )
    except Exception as httpx_exception:
        # Log the error and fall back to curl
        logger.error(f"HTTPX request failed: {httpx_exception}. Falling back to curl...")
        return fallback_to_curl(payload)


def fallback_to_curl(payload: dict) -> dict:
    """
    Fallback to curl if httpx fails.
    """
    # Validate FlyHub Base URL
    validate_url(FLYHUB_BASE_URL)

    # FlyHub API endpoint
    url = f"{FLYHUB_BASE_URL}/AirSearch"
    token = cached_token.get("token", None)

    if not token:
        raise HTTPException(
            status_code=500,
            detail="Cannot perform curl fallback: Missing authentication token.",
        )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"Authorization: {headers['Authorization']}",
            "-H", "Content-Type: application/json",
            "-d", payload_json,
        ]

        result = subprocess.run(curl_command, capture_output=True, text=True)

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}",
            )

        # Parse the curl response
        try:
            response_data = json.loads(result.stdout)
            logger.info("FlyHub response retrieved via curl fallback.")
            return response_data
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during the curl fallback: {str(e)}",
        )



# import requests
# import os
# import logging
# from fastapi import HTTPException

# class FlyhubClient:
#     def __init__(self):
#         self.base_url = "https://api.flyhub.com/api/v1"
#         self.username = os.getenv("FLYHUB_USERNAME")
#         self.apikey = os.getenv("FLYHUB_APIKEY")
#         self.token = self.authenticate()

# def authenticate(self):
#     # Ensure there are no extra quotes in the base URL or endpoint
#     url = f"{self.base_url}/Authenticate"
#     headers = {"Content-Type": "application/json"}
#     data = {"apikey": self.apikey}

#     try:
#         logging.info("Attempting to authenticate with BDFARE")
#         response = requests.post(url, headers=headers, json=data)
#         response.raise_for_status()  # Will raise HTTPError for bad responses
#         logging.debug(f"Authentication response: {response.json()}")  # Log full response for debugging
#         self.token = response.json().get("TokenId")
#         if not self.token:
#             raise ValueError("Token not found in authentication response.")
#         logging.info(f"Authentication successful, token received: {self.token}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")
#     except ValueError as e:
#         logging.error(f"Authentication failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

#     def get_balance(self):
#         url = f"{self.base_url}/GetBalance"
#         headers = {
#             "Authorization": f"Bearer {self.token}",
#             "Content-Type": "application/json"
#         }
#         data = {"UserName": self.username}
#         response = requests.post(url, headers=headers, json=data)
#         return response.json() if response.status_code == 200 else response.json()
