import time
import requests
from fastapi import HTTPException
import os

# FlyHub API credentials (from environment variables)
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


def get_flyhub_token() -> str:
    """
    Retrieve a valid token for FlyHub. If the cached token is expired or missing,
    request a new one.

    Returns:
        str: A valid FlyHub token.
    """
    global cached_token

    # Check if the cached token is still valid
    if cached_token["token"] and cached_token["expires_at"] > time.time():
        return cached_token["token"]

    # Request a new token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour (3600 seconds)
            cached_token["expires_at"] = time.time() + 3600
            return cached_token["token"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"FlyHub Authentication Failed: {response.text}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during FlyHub Authentication: {str(e)}"
        )
