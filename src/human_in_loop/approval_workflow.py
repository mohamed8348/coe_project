import sqlite3
import os
import uuid
import datetime
from typing import List, Dict, Any

class ApprovalWorkflow:
    HIGH_RISK_ACTIONS = ['DB Rollback', 'Workflow Reset', 'Financial Transaction Replay', 'Payroll Recalculation', 'Compliance Report Override']
    
    def __init__(self, db_path: str = 'data/approvals.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS approvals (
                id TEXT PRIMARY KEY,
                scenario_id TEXT,
                bug_id TEXT,
                action_type TEXT,
                risk_level TEXT,
                evidence_summary TEXT,
                decision TEXT,
                override_reason TEXT,
                decided_by TEXT,
                decided_at TEXT,
                created_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def submit_for_approval(self, scenario: Dict[str, Any], explanation: Dict[str, Any]) -> str:
        approval_id = str(uuid.uuid4())
        risk_level = scenario.get('risk_level', 'LOW')
        bug_id = scenario.get('bug_id', '')
        
        if risk_level == 'LOW':
            decision = 'APPROVED'
            decided_by = 'SYSTEM_AUTO'
            decided_at = datetime.datetime.utcnow().isoformat()
            print(f"Auto-approving LOW risk scenario for bug {bug_id}")
        else:
            decision = 'PENDING'
            decided_by = ''
            decided_at = ''
            print(f"Submitting {risk_level} risk scenario for bug {bug_id} for manual approval (Approval ID: {approval_id})")
            
        evidence_summary = explanation.get('explanation_text', '')
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO approvals 
            (id, scenario_id, bug_id, action_type, risk_level, evidence_summary, decision, override_reason, decided_by, decided_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            approval_id,
            scenario.get('scenario_id', ''),
            bug_id,
            scenario.get('fix_category', 'Unknown'),
            risk_level,
            evidence_summary,
            decision,
            '',
            decided_by,
            decided_at,
            datetime.datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return approval_id
        
    def decide(self, approval_id: str, decision: str, decided_by: str, override_reason: str = None) -> Dict[str, Any]:
        if decision not in ['APPROVED', 'REJECTED', 'OVERRIDDEN']:
            raise ValueError("Invalid decision")
            
        print(f"Recording decision '{decision}' for approval {approval_id} by {decided_by}")
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            UPDATE approvals
            SET decision = ?, decided_by = ?, decided_at = ?, override_reason = ?
            WHERE id = ?
        ''', (
            decision,
            decided_by,
            datetime.datetime.utcnow().isoformat(),
            override_reason or '',
            approval_id
        ))
        conn.commit()
        
        c.execute('SELECT * FROM approvals WHERE id = ?', (approval_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'scenario_id': row[1],
                'bug_id': row[2],
                'decision': row[6]
            }
        return {}
        
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM approvals WHERE decision = 'PENDING'")
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def get_approval_history(self, bug_id: str = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        if bug_id:
            c.execute("SELECT * FROM approvals WHERE bug_id = ? ORDER BY created_at DESC", (bug_id,))
        else:
            c.execute("SELECT * FROM approvals ORDER BY created_at DESC")
            
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]
