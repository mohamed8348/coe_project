import uuid
import datetime
from typing import List, Dict, Any

class ScenarioGenerator:
    def generate(self, bug_dict: Dict[str, Any], retrieved_cases: List[Dict[str, Any]], log_keywords: List[str], screenshot_features: Dict[str, Any]) -> Dict[str, Any]:
        bug_id = bug_dict.get('bug_id', 'UNKNOWN')
        module = bug_dict.get('module', 'UNKNOWN')
        severity = bug_dict.get('severity', 'Medium')
        fix_category = bug_dict.get('fix_category', 'Unknown')
        
        steps = [f"Log in to the system", f"Navigate to the {module} module", f"Trigger the action related to {bug_id}"]
        
        critical_fixes = ['DB Rollback', 'Workflow Reset', 'Financial Transaction Replay', 'Payroll Recalculation']
        
        risk_level = 'LOW'
        if fix_category in critical_fixes:
            risk_level = 'CRITICAL'
        elif severity == 'Critical' or 'Exception' in ' '.join(log_keywords):
            risk_level = 'HIGH'
        elif severity == 'High':
            risk_level = 'MEDIUM'
            
        requires_approval = risk_level in ['HIGH', 'CRITICAL']
        
        gherkin = f"Feature: Reproduce bug {bug_id}\n\nScenario: System handles {bug_id}\n"
        for i, step in enumerate(steps):
            prefix = "Given" if i == 0 else ("When" if i == 1 else "And")
            gherkin += f"  {prefix} {step.lower()}\n"
        
        gherkin += f"  Then the system should behave correctly\n"
        
        return {
            'scenario_id': str(uuid.uuid4()),
            'bug_id': bug_id,
            'module': module,
            'generated_steps': steps,
            'expected_result': 'The action completes without errors',
            'actual_result': 'An error occurs or incorrect data is saved',
            'confidence_score': 0.85,
            'source_cases': [c.get('bug_id') for c in retrieved_cases if 'bug_id' in c],
            'risk_level': risk_level,
            'requires_approval': requires_approval,
            'gherkin': gherkin,
            'generated_at': datetime.datetime.utcnow().isoformat()
        }
