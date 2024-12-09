from app.flight_services.models.airprice.airprice_response import AirPriceResponse, AirPriceDetails, AirPriceSegment

def adapt_bdfare_response(raw_data, trace_id):
    offers = raw_data.get("response", {}).get("offersGroup", [])
    prices = []
    
    for offer in offers:
        offer_data = offer.get("offer", {})
        segments = [
            AirPriceSegment(
                from_=segment["departure"]["iatA_LocationCode"],
                to=segment["arrival"]["iatA_LocationCode"],
                departureTime=segment["departure"]["aircraftScheduledDateTime"],
                arrivalTime=segment["arrival"]["aircraftScheduledDateTime"],
                airline=segment["marketingCarrierInfo"]["carrierDesigCode"],
                flightNumber=segment["flightNumber"],
                cabinClass=segment["cabinType"],
                durationMinutes=int(segment["duration"])
            )
            for pax_segment in offer_data.get("paxSegmentList", [])
            for segment in pax_segment.get("paxSegment", [])
        ]
        prices.append(
            AirPriceDetails(
                totalFare=offer_data["price"]["totalPayable"]["total"],
                currency=offer_data["price"]["totalPayable"]["curreny"],
                refundable=offer_data["refundable"],
                segments=segments
            )
        )
    return AirPriceResponse(traceId=trace_id, prices=prices)
