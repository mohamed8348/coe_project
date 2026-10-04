from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas import ScenarioOutput

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios"])

# Import mock DB from bugs router
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
        "explanation_text": (
            f"This scenario was generated for module "
            f"{scenario['module']} with confidence "
            f"{scenario['confidence_score'] * 100:.0f}%."
        ),
        "evidence": [
            {
                "type": "historical_match",
                "description": "Matched similar ERP incidents from historical bug reports."
            },
            {
                "type": "module_analysis",
                "description": f"Module {scenario['module']} has known recurring issue patterns."
            },
            {
                "type": "confidence",
                "description": f"Scenario confidence score = {scenario['confidence_score']}"
            }
        ]
    }


@router.get("/{scenario_id}/tests", response_model=Dict[str, str])
async def get_scenario_tests(scenario_id: str):
    if scenario_id not in scenarios_db:
        raise HTTPException(status_code=404, detail="Scenario not found")

    scenario = scenarios_db[scenario_id]

    return {
        "gherkin": scenario.get("gherkin", ""),
        "selenium": """
def test_selenium():
    pass
""",
        "playwright": """
test('playwright test', async ({ page }) => {
});
""",
        "postman": """
{
  "info": {
    "name": "ERP Test Collection"
  }
}
"""
    }