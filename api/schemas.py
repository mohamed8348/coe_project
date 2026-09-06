from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Priority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class DecisionType(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    OVERRIDDEN = "OVERRIDDEN"

class BugReportInput(BaseModel):
    bug_id: str
    title: str
    description: str
    severity: Severity
    priority: Priority
    module: str
    reporter_role: str
    report_date: datetime
    os: Optional[str] = None
    browser: Optional[str] = None
    erp_version: Optional[str] = None
    db_version: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    log_content: Optional[str] = None
    ui_page: Optional[str] = None
    visible_fields: Optional[List[str]] = None
    user_action: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None

class ScenarioOutput(BaseModel):
    scenario_id: str
    bug_id: str
    module: str
    generated_steps: List[str]
    expected_result: str
    actual_result: str
    confidence_score: float
    risk_level: str
    requires_approval: bool
    gherkin: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class ApprovalDecisionInput(BaseModel):
    decision: DecisionType
    decided_by: str
    override_reason: Optional[str] = None

class ApprovalOutput(BaseModel):
    approval_id: str
    scenario_id: str
    bug_id: str
    risk_level: str
    evidence_summary: str
    decision: DecisionType
    decided_at: datetime = Field(default_factory=datetime.utcnow)

class EvaluationReport(BaseModel):
    rsr: float
    precision: float
    recall: float
    f1: float
    completeness: float
    time_saved_hours: float
    error_analysis: dict
