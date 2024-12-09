from typing import List
from app.flight_services.models.rules_response import Rule

def transform_bdfare_rules(response: dict) -> List[Rule]:
    if "error" in response["response"]:
        return []

    rules = []
    for route_info in response["response"].get("fareRuleRouteInfos", []):
        for pax_info in route_info.get("fareRulePaxInfos", []):
            for rule in pax_info.get("fareRuleInfos", []):
                rules.append(
                    Rule(
                        paxType=pax_info.get("paxType"),
                        cityPair=route_info.get("route"),
                        ruleType=rule.get("category"),
                        ruleDetails=rule.get("info"),
                    )
                )
    return rules

def transform_flyhub_rules(response: dict, rule_type: str) -> List[Rule]:
    transformed_rules = []

    for rule in response:
        transformed_rules.append(
            Rule(
                paxType=rule.get("Paxtype"),
                cityPair=rule.get("CityPair"),
                ruleType=rule.get("RuleType"),
                ruleDetails=rule.get("RuleDetails"),
            )
        )

    return transformed_rules

