from fastapi import APIRouter, HTTPException
import httpx
import os
import time

router = APIRouter()

# Fetch FlyHub API credentials from environment variables
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")
FLYHUB_PRODUCTION_URL = os.getenv("FLYHUB_PRODUCTION_URL", "https://api.flyhub.com/api/v1/")

# Ensure mandatory environment variables are set
if not FLYHUB_USERNAME or not FLYHUB_API_KEY:
    raise ValueError("Missing required FlyHub API credentials in the environment variables.")

# Token cache
cached_token = {"token": None, "expires_at": 0}


@router.post("/authenticate")
async def authenticate():
    """
    Authenticate with FlyHub API to get a Bearer token.

    Returns:
        dict: Contains the Bearer token and expiration time.
    """
    global cached_token
    url = f"{FLYHUB_PRODUCTION_URL}Authenticate"
    payload = {
        "username": FLYHUB_USERNAME,
        "apikey": FLYHUB_API_KEY
    }

    try:
        # Make the authentication request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()

            # Cache the token and expiration time
            cached_token["token"] = token_data.get("TokenId")
            cached_token["expires_at"] = time.time() + 3600  # Default to 1 hour (3600 seconds)

            # Return the token and expiration info
            return {
                "token": cached_token["token"],
                "expires_at": cached_token["expires_at"],
                "status": "Success"
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with FlyHub API: {exc}")
