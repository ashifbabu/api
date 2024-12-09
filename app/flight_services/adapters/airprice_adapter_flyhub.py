from app.flight_services.models.airprice.airprice_response import AirPriceResponse, AirPriceDetails, AirPriceSegment


def convert_bdfare_to_flyhub_airprice_request(payload: dict) -> dict:
    """
    Convert a BDFare-compatible AirPrice request payload to FlyHub-compatible payload.
    
    Args:
        payload (dict): The unified request payload.
    
    Returns:
        dict: Transformed payload for FlyHub.
    """
    try:
        return {
            "SearchID": payload.get("traceId"),  # Map BDFare traceId to FlyHub SearchID
            "ResultID": payload.get("offerId", [])[0]  # Use the first offerId for ResultID
        }
    except KeyError as e:
        raise ValueError(f"Missing required key in payload: {e}")


def adapt_flyhub_response(raw_data, search_id):
    """
    Adapt FlyHub raw response data into a unified AirPriceResponse format.

    Args:
        raw_data (dict): The raw response data from FlyHub.
        search_id (str): The search ID for tracking the request.

    Returns:
        AirPriceResponse: A unified response containing adapted price details and segments.
    """
    results = raw_data.get("Results", [])
    prices = []

    for result in results:
        segments = [
            AirPriceSegment(
                from_=segment["Origin"]["Airport"]["AirportCode"],
                to=segment["Destination"]["Airport"]["AirportCode"],
                departureTime=segment["Origin"]["DepTime"],
                arrivalTime=segment["Destination"]["ArrTime"],
                airline=segment["Airline"]["AirlineCode"],
                flightNumber=segment["Airline"]["FlightNumber"],
                cabinClass=segment["Airline"]["CabinClass"],
                durationMinutes=int(segment["JourneyDuration"]) if segment.get("JourneyDuration") else 0
            )
            for segment in result.get("segments", [])
        ]

        prices.append(
            AirPriceDetails(
                totalFare=result.get("TotalFare", 0),
                currency=result.get("Currency", "USD"),
                refundable=result.get("IsRefundable", False),
                segments=segments
            )
        )

    # Handle cases where the response may not have valid results
    if not prices:
        prices = []

    return AirPriceResponse(traceId=search_id, prices=prices)
