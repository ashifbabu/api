from fastapi import APIRouter, Query
from .models import HotelSearchRequest

hotel_router = APIRouter()

@hotel_router.get("/search")
def search_hotels(location: str = Query(...), check_in: str = Query(...), check_out: str = Query(...), guests: int = Query(...)):
    # Placeholder for hotel search logic
    return {"message": "Hotel search results", "location": location, "check_in": check_in, "check_out": check_out, "guests": guests}

@hotel_router.get("/{hotel_id}")
def get_hotel_details(hotel_id: int):
    # Placeholder for retrieving hotel details
    return {"message": "Hotel details", "hotel_id": hotel_id}

