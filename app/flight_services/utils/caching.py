from typing import Any, Dict
from functools import lru_cache
import requests

airport_cache: Dict[str, str] = {}


@lru_cache(maxsize=100)
def get_airport_name(iata_code: str) -> str:
    """
    Retrieve the name of an airport given its IATA code.
    Uses caching to minimize redundant API calls.

    Args:
        iata_code (str): The IATA code of the airport.

    Returns:
        str: The name of the airport.
    """
    if iata_code in airport_cache:
        return airport_cache[iata_code]

    # Replace this with your actual API endpoint for airport data
    url = f"https://port-api.com/port/code/{iata_code}"

    try:
        response = requests.get(url, headers={"accept": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data["features"]:
                airport_name = data["features"][0]["properties"]["name"]
                airport_cache[iata_code] = airport_name
                return airport_name
        return "Unknown Airport"
    except Exception:
        return "Unknown Airport"
