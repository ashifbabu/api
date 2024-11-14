from fastapi import FastAPI
from app.flight_services.routes.flyhub import balance as flyhub_balance_routes
from app.flight_services.routes.bdfare import balance as bdfare_balance_routes
from app.hotel_services.routes import hotel_router
from app.bus_services.routes import bus_router
from app.car_services.routes import car_router
from app.event_services.routes import event_router
from app.holidays_services.routes import holiday_router
from app.insurance_services.routes import insurance_router
from app.train_services.routes import train_router

app = FastAPI(
    title="Travel API",
    version="1.0.0",
    openapi_url="/openapi.json",
    description="API for flight and travel related services"
)

# Include service routers with appropriate prefixes and tags
app.include_router(flyhub_balance_routes.router, prefix="/api/flyhub", tags=["Flights"])
app.include_router(bdfare_balance_routes.router, prefix="/api/bdfare", tags=["Flights"])
app.include_router(hotel_router, prefix="/hotels", tags=["Hotels"])
app.include_router(bus_router, prefix="/bus", tags=["Bus"])
app.include_router(car_router, prefix="/cars", tags=["Cars"])
app.include_router(event_router, prefix="/events", tags=["Events"])
app.include_router(holiday_router, prefix="/holidays", tags=["Holidays"])
app.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
app.include_router(train_router, prefix="/trains", tags=["Trains"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Travel API!"}
