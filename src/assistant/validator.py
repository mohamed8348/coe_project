from typing import Tuple, List, Dict, Any

class ScenarioValidator:
    def validate(self, scenario: Dict[str, Any]) -> Tuple[bool, List[str]]:
        issues = []
        
        steps = scenario.get('generated_steps', [])
        if not steps:
            issues.append("generated_steps is empty")
        elif len(steps) < 3:
            issues.append("generated_steps must contain at least 3 steps")
            
        if not scenario.get('expected_result'):
            issues.append("expected_result is empty")
            
        if not scenario.get('actual_result'):
            issues.append("actual_result is empty")
            
        gherkin = scenario.get('gherkin', '')
        if 'Given ' not in gherkin or 'When ' not in gherkin or 'Then ' not in gherkin:
            issues.append("Gherkin text must contain 'Given', 'When', and 'Then'")
            
        return len(issues) == 0, issues
