#app\flight_services\adapters\flyhub_adapter.py
from typing import Dict, Any
from app.flight_services.models.combined.combined_search import (
    FlightSearchResponse,
    FlightSegment,
    PriceDetails,
    BaggageDetails,
)

def convert_bdfare_to_flyhub(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert BDFare request format to FlyHub request format.
    """
    trip_type = payload["shoppingCriteria"]["tripType"].lower()
    journey_type = "1" if trip_type == "oneway" else "2" if trip_type == "return" else "3"

    segments = [
        {
            "Origin": segment["originDepRequest"]["iatA_LocationCode"],
            "Destination": segment["destArrivalRequest"]["iatA_LocationCode"],
            "CabinClass": "1" if payload["shoppingCriteria"]["travelPreferences"]["cabinCode"].lower() == "economy" else "2",
            "DepartureDateTime": segment["originDepRequest"]["date"]
        }
        for segment in payload.get("originDest", [])
    ]

    return {
        "AdultQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "ADT"),
        "ChildQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "CHD"),
        "InfantQuantity": sum(1 for pax in payload.get("pax", []) if pax.get("ptc") == "INF"),
        "EndUserIp": "103.124.251.147",  # Replace with dynamic IP if needed
        "JourneyType": journey_type,
        "Segments": segments,
    }
def simplify_flyhub_response(response: Dict[str, Any]) -> FlightSearchResponse:
    """Simplify FlyHub response into Unified Data Model."""
    simplified_results = []

    for result in response.get("Results", []):
        segments = []
        for segment in result.get("segments", []):
            segments.append(FlightSegment(
                from_=segment["Origin"]["Airport"]["AirportCode"],
                fromAirportName=segment["Origin"]["Airport"]["AirportName"],
                to=segment["Destination"]["Airport"]["AirportCode"],
                toAirportName=segment["Destination"]["Airport"]["AirportName"],
                departureTime=segment["Origin"]["DepTime"],
                arrivalTime=segment["Destination"]["ArrTime"],
                airlineCode=segment["Airline"]["AirlineCode"],
                airlineName=segment["Airline"]["AirlineName"],
                flightNumber=segment["Airline"]["FlightNumber"],
                cabinClass=segment["Airline"]["CabinClass"],
                durationMinutes=segment["JourneyDuration"],
            ))

        simplified_results.append(FlightSearchResponse(
            id=result["ResultID"],
            airline=result["Validatingcarrier"],
            airlineName=result["ValidatingcarrierName"],
            refundable=result["IsRefundable"],
            fareType=result["FareType"],
            price=PriceDetails(
                baseFare=result["Fares"][0]["BaseFare"],
                tax=result["Fares"][0]["Tax"],
                discount=result["Fares"][0]["Discount"],
                total=result["Fares"][0]["BaseFare"] + result["Fares"][0]["Tax"] - result["Fares"][0]["Discount"],
                currency=result["Fares"][0]["Currency"],
            ),
            segments=segments,
            baggageAllowance=[
                BaggageDetails(
                    from_=segment["Origin"]["Airport"]["AirportCode"],
                    to=segment["Destination"]["Airport"]["AirportCode"],
                    checkIn=baggage.get("Checkin"),
                    cabin=baggage.get("Cabin"),
                )
                for segment in result.get("segments", [])
                for baggage in segment.get("baggageDetails", [])
            ],
            seatsRemaining=result.get("Availabilty", 0),
        ))

    return simplified_results
