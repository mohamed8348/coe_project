from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas import BugReportInput, ScenarioOutput
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/bugs", tags=["Bugs"])

# Mock DB for prototype
bugs_db = {}
scenarios_db = {}

@router.post("/ingest", response_model=ScenarioOutput)
async def ingest_bug(bug: BugReportInput):
    # Store bug
    bugs_db[bug.bug_id] = bug.model_dump()
    
    # Mocking pipeline: ingestion -> cleaning -> feature extraction -> retrieval -> scenario generation -> validation
    scenario_id = str(uuid.uuid4())
    scenario = ScenarioOutput(
        scenario_id=scenario_id,
        bug_id=bug.bug_id,
        module=bug.module,
        generated_steps=["Navigate to login", "Enter credentials", f"Go to {bug.module}"],
        expected_result=bug.expected_behavior or "System functions normally",
        actual_result=bug.actual_behavior or "Error occurred",
        confidence_score=0.85,
        risk_level="MEDIUM",
        requires_approval=True,
        gherkin=f"Feature: Reproduce {bug.bug_id}\\n  Scenario: Auto-generated\\n    Given user is on {bug.ui_page}"
    )
    scenarios_db[scenario_id] = scenario.model_dump()
    
    return scenario

@router.get("/{bug_id}", response_model=Dict[str, Any])
async def get_bug(bug_id: str):
    if bug_id not in bugs_db:
        raise HTTPException(status_code=404, detail="Bug not found")
    return bugs_db[bug_id]

@router.get("/", response_model=List[Dict[str, Any]])
async def list_bugs(skip: int = 0, limit: int = 10):
    return list(bugs_db.values())[skip:skip+limit]
