import json
import subprocess
import asyncio
from typing import Dict, Any
from fastapi import HTTPException
import httpx
import os

# Load API credentials from environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")
FLYHUB_BASE_URL = os.getenv("FLYHUB_PRODUCTION_URL")
FLYHUB_USERNAME = os.getenv("FLYHUB_USERNAME")
FLYHUB_API_KEY = os.getenv("FLYHUB_API_KEY")

# Cached token for FlyHub
cached_token = {"token": None, "expires_at": 0}


async def fetch_bdfare_flights(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call BDFare API for flight searching with a fallback to curl."""
    url = f"{BDFARE_BASE_URL}/AirShopping"
    headers = {"X-API-KEY": BDFARE_API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        # Fallback to curl
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"X-API-KEY: {BDFARE_API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", payload_json,
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )


async def fetch_flyhub_flights(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Call FlyHub API for flight searching with a fallback to curl."""
    global cached_token
    if not cached_token["token"] or cached_token["expires_at"] <= asyncio.get_event_loop().time():
        await authenticate_flyhub()

    url = f"{FLYHUB_BASE_URL}/AirSearch"
    headers = {
        "Authorization": f"Bearer {cached_token['token']}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        # Fallback to curl
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", f"Authorization: Bearer {cached_token['token']}",
            "-H", "Content-Type: application/json",
            "-d", payload_json,
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )


async def authenticate_flyhub():
    """Authenticate with FlyHub and cache the token."""
    global cached_token
    url = f"{FLYHUB_BASE_URL}/Authenticate"
    payload = {"username": FLYHUB_USERNAME, "apikey": FLYHUB_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            token_data = response.json()
            cached_token["token"] = token_data["TokenId"]
            # Assume token validity is 1 hour
            cached_token["expires_at"] = asyncio.get_event_loop().time() + 3600
        else:
            raise HTTPException(status_code=response.status_code, detail="FlyHub Authentication Failed")
    except Exception as e:
        # Fallback to curl for authentication
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST",
            url,
            "-H", "Content-Type: application/json",
            "-d", payload_json,
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Curl command failed: {result.stderr}"
            )
        try:
            token_data = json.loads(result.stdout)
            cached_token["token"] = token_data["TokenId"]
            cached_token["expires_at"] = asyncio.get_event_loop().time() + 3600
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to decode JSON response from curl: {result.stdout}"
            )
