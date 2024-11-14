import requests
import os
import logging
from fastapi import HTTPException

class BDFAREClient:
    def __init__(self):
        # Read environment variables
        self.base_url = os.getenv("BDFARE_BASE_URL")
        self.apikey = os.getenv("BDFARE_API_KEY")
        self.token = None
        
        # Ensure that the required environment variables are set
        if not self.base_url or not self.apikey:
            logging.error("BDFARE_BASE_URL or BDFARE_API_KEY is not set in the environment variables.")
            raise HTTPException(status_code=500, detail="API configuration is missing")

        logging.info("Initializing BDFAREClient")
        self.authenticate()

    def authenticate(self):
        url = f"{self.base_url}/Authenticate"
        headers = {"Content-Type": "application/json"}
        data = {"apikey": self.apikey}

        try:
            logging.info("Attempting to authenticate with BDFARE")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Will raise HTTPError for bad responses
            logging.debug(f"Authentication response: {response.json()}")  # Log full response for debugging
            self.token = response.json().get("TokenId")
            if not self.token:
                raise ValueError("Token not found in authentication response.")
            logging.info(f"Authentication successful, token received: {self.token}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Authentication failed: {e}")
            raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")
        except ValueError as e:
            logging.error(f"Authentication failed: {e}")
            raise HTTPException(status_code=500, detail=f"Authentication failed: {e}")

    def get_balance(self):
        if not self.token:
            logging.info("Token missing, re-authenticating.")
            self.authenticate()

        url = f"{self.base_url}/GetBalance"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {"UserName": self.apikey}  # Confirm payload structure from API documentation

        try:
            logging.info("Requesting balance from BDFARE")
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Check for HTTP errors
            logging.debug(f"Balance response: {response.json()}")  # Log full response for debugging
            logging.info("Balance request successful")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get balance: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get balance: {e}")
