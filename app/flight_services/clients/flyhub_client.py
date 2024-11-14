import requests
import os

class FlyhubClient:
    def __init__(self):
        self.base_url = "https://api.flyhub.com/api/v1"
        self.username = os.getenv("FLYHUB_USERNAME")
        self.apikey = os.getenv("FLYHUB_APIKEY")
        self.token = self.authenticate()

def authenticate(self):
    # Ensure there are no extra quotes in the base URL or endpoint
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
        url = f"{self.base_url}/GetBalance"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {"UserName": self.username}
        response = requests.post(url, headers=headers, json=data)
        return response.json() if response.status_code == 200 else response.json()
