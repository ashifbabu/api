from fastapi import APIRouter, HTTPException, Body
from app.flight_services.models.rules_request import RulesRequest
from app.flight_services.models.rules_response import RulesResponse
from app.flight_services.clients.rules_client import fetch_bdfare_rules, fetch_flyhub_rules, transform_to_bdfare_request
from app.flight_services.transformers.rules_transformer import transform_bdfare_rules, transform_flyhub_rules

router = APIRouter()

@router.post("/airrules", response_model=RulesResponse)
async def get_rules(payload: RulesRequest = Body(...)):
    """
    Fetch fare or mini rules from BDFare or FlyHub.
    """
    source = payload.source
    rule_type = payload.rule_type
    data = payload.data

    try:
        if source == "bdfare":
            # Transform data to match BDFare's required format
            bdfare_data = transform_to_bdfare_request(data)
            
            # Determine the endpoint
            endpoint = "MiniRule" if rule_type == "mini" else "FareRules"
            
            # Call BDFare API
            response = await fetch_bdfare_rules(endpoint, bdfare_data)
            
            # Transform the response
            rules = transform_bdfare_rules(response)
        
        elif source == "flyhub":
            endpoint = "AirMiniRules" if rule_type == "mini" else "AirRules"
            response = await fetch_flyhub_rules(endpoint, data)
            rules = transform_flyhub_rules(response, rule_type)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid source")

        return RulesResponse(source=source, rules=rules, error=None)
    
    except Exception as e:
        return RulesResponse(source=source, rules=[], error=str(e))
