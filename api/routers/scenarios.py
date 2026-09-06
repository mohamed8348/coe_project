from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas import ScenarioOutput

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])

# Rely on the mock DB from bugs router for demonstration
from .bugs import scenarios_db

@router.get("/{scenario_id}", response_model=ScenarioOutput)
async def get_scenario(scenario_id: str):
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenarios_db[scenario_id]

@router.get("/{scenario_id}/explanation", response_model=Dict[str, Any])
async def get_scenario_explanation(scenario_id: str):
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail="Scenario not found")
    scenario = scenarios_db[scenario_id]
    return {
        "scenario_id": scenario_id,
        "factors": ["High similarity to past bugs", "Module historical failure rate"],
        "confidence_breakdown": {"retrieval": 0.9, "generation": 0.8}
    }

@router.get("/{scenario_id}/tests", response_model=Dict[str, str])
async def get_scenario_tests(scenario_id: str):
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail="Scenario not found")
    scenario = scenarios_db[scenario_id]
    
    return {
        "gherkin": scenario.get('gherkin', ''),
        "selenium": "def test_selenium():\n    pass",
        "playwright": "test('playwright test', async ({ page }) => {});",
        "postman": "{ 'info': { 'name': 'test' } }"
    }
