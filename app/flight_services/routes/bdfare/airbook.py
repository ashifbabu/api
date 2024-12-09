from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
import subprocess
import json
from dotenv import load_dotenv
import logging
from typing import Optional
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
class AssociatePax(BaseModel):
    givenName: str = Field(..., example="John")
    surname: str = Field(..., example="Wick")

class LoyaltyProgramAccount(BaseModel):
    airlineDesigCode: str = Field(..., example="BS")
    accountNumber: str = Field(..., example="3523626235")


class SellSSR(BaseModel):
    ssrRemark: str = Field(default="", example="")
    ssrCode: str = Field(..., example="WCHR")
    loyaltyProgramAccount: Optional[LoyaltyProgramAccount] = None


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
    associatePax: Optional[AssociatePax] = None   # Make this field optional

class PaxList(BaseModel):
    ptc: str = Field(..., example="Adult")
    individual: Individual
    sellSSR: Optional[List[SellSSR]] = None


class Phone(BaseModel):
    phoneNumber: str = Field(..., example="1234567")
    countryDialingCode: str = Field(..., example="880")


class ContactInfo(BaseModel):
    phone: Phone
    emailAddress: str = Field(..., example="abc@xyz.com")


class AirBookRequestPayload(BaseModel):
    contactInfo: ContactInfo
    paxList: List[PaxList]


class AirBookRequest(BaseModel):
    traceId: str = Field(..., example="cd0cd824-c6bd-4025-893c-ccf4577dd454")
    offerId: List[str] = Field(..., example=["string"])
    request: AirBookRequestPayload


class AirBookResponse(BaseModel):
    success: bool
    data: Dict[str, Any]


@router.post(
    "/airbook",
    response_model=AirBookResponse,
    summary="Create Booking",
    description="Create a new air booking using the BDFare API.",
)
async def create_booking(payload: AirBookRequest):
    """
    Create a new air booking using BDFare API with curl.

    Args:
        payload (AirBookRequest): The air booking request payload.

    Returns:
        AirBookResponse: The response from the BDFare API.
    """
    if not BDFARE_BASE_URL:
        logger.error("BDFare Base URL is missing.")
        raise HTTPException(status_code=500, detail="BDFare Base URL is not configured.")
    if not BDFARE_API_KEY:
        logger.error("BDFare API Key is missing.")
        raise HTTPException(status_code=500, detail="BDFare API key is not configured.")

    url = f"{BDFARE_BASE_URL}/OrderCreate"

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

        return AirBookResponse(success=True, data=response_data)

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
