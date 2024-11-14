from fastapi import APIRouter
from app.flight_services.routes.flyhub.auth import router as flyhub_auth_router
from app.flight_services.routes.flyhub.balance import router as flyhub_balance_router

flight_router = APIRouter()

# Include Flyhub routers under the flights section
flight_router.include_router(
    flyhub_auth_router, 
    prefix="/api/flyhub/auth",
    tags=["Flights"]
)
flight_router.include_router(
    flyhub_balance_router, 
    prefix="/api/flyhub/balance",
    tags=["Flights"]
)
