from fastapi import APIRouter, Query
from .models import HolidaySearchRequest

holiday_router = APIRouter()

@holiday_router.get("/search")
def search_holidays(destination: str = Query(...), start_date: str = Query(...), end_date: str = Query(...), budget: float = Query(...)):
    # Placeholder for holiday package search logic
    return {"message": "Holiday package search results", "destination": destination, "start_date": start_date, "end_date": end_date, "budget": budget}

@holiday_router.get("/{package_id}")
def get_holiday_package_details(package_id: int):
    # Placeholder for retrieving holiday package details
    return {"message": "Holiday package details", "package_id": package_id}
