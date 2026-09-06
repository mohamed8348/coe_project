from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..schemas import ApprovalDecisionInput, ApprovalOutput
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/approvals", tags=["Approvals"])

# Mock DB
approvals_db = {}
pending_approvals = [
    {"scenario_id": "scen-1", "bug_id": "BUG-100", "risk_level": "HIGH", "evidence_summary": "Modifies financial records"}
]

@router.get("/pending", response_model=List[Dict[str, Any]])
async def get_pending_approvals():
    return pending_approvals

@router.post("/{approval_id}/decide", response_model=ApprovalOutput)
async def decide_approval(approval_id: str, decision: ApprovalDecisionInput):
    output = ApprovalOutput(
        approval_id=approval_id,
        scenario_id="mock-scen",
        bug_id="mock-bug",
        risk_level="HIGH",
        evidence_summary="Approved by human",
        decision=decision.decision,
        decided_at=datetime.utcnow()
    )
    approvals_db[approval_id] = output.model_dump()
    return output

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_approval_history():
    return list(approvals_db.values())
