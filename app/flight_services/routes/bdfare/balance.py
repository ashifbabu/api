from fastapi import APIRouter, HTTPException, Depends
import httpx
import os

router = APIRouter()

# Read environment variables
BDFARE_BASE_URL = os.getenv("BDFARE_BASE_URL")
BDFARE_API_KEY = os.getenv("BDFARE_API_KEY")


@router.get("/balance")
async def get_balance():
    """
    Retrieve account balance from BDFare.

    Returns:
        dict: The response from the BDFare GetBalance API.
    """
    if not BDFARE_BASE_URL or not BDFARE_API_KEY:
        raise HTTPException(status_code=500, detail="BDFare configuration is missing in environment variables.")

    url = f"{BDFARE_BASE_URL}/GetBalance"
    headers = {
        "X-API-KEY": BDFARE_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        # Make a GET request to the BDFare API
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error communicating with BDFare API: {exc}")
