from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class FailureResult:
    case_id: str
    failure_type: str
    detected: bool
    detection_reason: str
    fallback_applied: str
    recovery_output: dict
    confidence_penalty: float
    requires_human_review: bool

class FailureStateHandler:
    """Handles specific failure cases during scenario generation."""
    
    def handle_missing_logs(self, log_content: Optional[str], scenario_data: dict) -> FailureResult:
        detected = not log_content or log_content.strip() == 'NO_LOG_AVAILABLE'
        recovery_output = dict(scenario_data)
        confidence_penalty = 0.0
        reason = "Logs available."
        fallback = "None"
        
        if detected:
            reason = "Log content is empty, null, or NO_LOG_AVAILABLE"
            fallback = "Use module-specific default log patterns for initial triage"
            confidence_penalty = 0.40
            
            warning = 'INCOMPLETE: No logs available. Steps generated from description only.'
            if 'warnings' not in recovery_output:
                recovery_output['warnings'] = []
            recovery_output['warnings'].append(warning)
            
            # Reduce confidence score if present
            if 'confidence_score' in recovery_output:
                recovery_output['confidence_score'] *= (1.0 - confidence_penalty)
                
        return FailureResult(
            case_id="case_1",
            failure_type="Missing Logs",
            detected=detected,
            detection_reason=reason,
            fallback_applied=fallback,
            recovery_output=recovery_output,
            confidence_penalty=confidence_penalty,
            requires_human_review=False
        )

    def handle_corrupted_screenshot(self, ui_page: str, visible_fields: str, user_action: str, scenario_data: dict) -> FailureResult:
        detected = (ui_page == 'UNKNOWN' and visible_fields == 'UNKNOWN' and user_action == 'UNKNOWN')
        recovery_output = dict(scenario_data)
        confidence_penalty = 0.0
        reason = "Screenshot metadata is valid."
        fallback = "None"
        
        if detected:
            reason = "ui_page, visible_fields, and user_action are UNKNOWN"
            fallback = "Rely solely on description and logs for scenario generation"
            recovery_output['screenshot_used'] = False
            
            note = "Screenshot metadata was corrupted or missing."
            if 'explanation_notes' not in recovery_output:
                recovery_output['explanation_notes'] = []
            recovery_output['explanation_notes'].append(note)
            
        return FailureResult(
            case_id="case_2",
            failure_type="Corrupted Screenshot Metadata",
            detected=detected,
            detection_reason=reason,
            fallback_applied=fallback,
            recovery_output=recovery_output,
            confidence_penalty=confidence_penalty,
            requires_human_review=False
        )

    def handle_contradictory_env(self, browser: str, os: str, erp_version: str, db_version: str, scenario_data: dict) -> FailureResult:
        compatibility_matrix = {
            'v12.x': ['PostgreSQL 13', 'Oracle 19c'],
            'v13.x': ['PostgreSQL 14', 'SQL Server 2019'],
            'v14.x': ['PostgreSQL 14']
        }
        
        contradictions = []
        if browser.lower() == 'safari' and 'windows' in os.lower():
            contradictions.append(f"Safari is not available on {os}")
            
        if erp_version in compatibility_matrix:
            if db_version not in compatibility_matrix[erp_version]:
                contradictions.append(f"{db_version} is not compatible with {erp_version}")
                
        detected = len(contradictions) > 0
        recovery_output = dict(scenario_data)
        confidence_penalty = 0.0
        reason = "Environment details are consistent."
        fallback = "None"
        requires_review = False
        
        if detected:
            reason = f"Contradictions found: {', '.join(contradictions)}"
            fallback = "Generate scenario for each plausible environment variant"
            requires_review = True
            recovery_output['env_contradiction'] = True
            recovery_output['contradiction_details'] = contradictions
            recovery_output['variants'] = ['Variant A (Windows/Edge)', 'Variant B (Mac/Safari)']
            
        return FailureResult(
            case_id="case_3",
            failure_type="Contradictory Environment Details",
            detected=detected,
            detection_reason=reason,
            fallback_applied=fallback,
            recovery_output=recovery_output,
            confidence_penalty=confidence_penalty,
            requires_human_review=requires_review
        )

    def handle_multiple_root_causes(self, top_cases: List[dict], scenario_data: dict) -> FailureResult:
        detected = False
        reason = "Single definitive root cause or distinct scores."
        fallback = "None"
        requires_review = False
        recovery_output = dict(scenario_data)
        
        if len(top_cases) >= 2:
            score1 = top_cases[0].get('score', 0)
            score2 = top_cases[1].get('score', 0)
            cat1 = top_cases[0].get('fix_category', '')
            cat2 = top_cases[1].get('fix_category', '')
            
            if abs(score1 - score2) <= 0.08 and cat1 != cat2:
                detected = True
                reason = "Top-2 retrieved cases have similarity scores within 0.08 and different fix categories"
                fallback = "Return multiple candidate scenarios"
                requires_review = True
                
                recovery_output['candidate_scenarios'] = [
                    {'root_cause': cat1, 'confidence': score1},
                    {'root_cause': cat2, 'confidence': score2}
                ]
                
        return FailureResult(
            case_id="case_4",
            failure_type="Multiple Possible Root Causes",
            detected=detected,
            detection_reason=reason,
            fallback_applied=fallback,
            recovery_output=recovery_output,
            confidence_penalty=0.0,
            requires_human_review=requires_review
        )

    def handle_no_historical_match(self, best_score: float, scenario_data: dict) -> FailureResult:
        detected = best_score < 0.35
        reason = "Valid historical match found."
        fallback = "None"
        confidence_penalty = 0.0
        recovery_output = dict(scenario_data)
        
        if detected:
            reason = f"Best FAISS similarity score ({best_score}) < 0.35"
            fallback = "Fall back to module-level template generation"
            
            recovery_output['fallback_used'] = True
            recovery_output['confidence_score'] = 0.25
            
        return FailureResult(
            case_id="case_5",
            failure_type="No Historical Match Found",
            detected=detected,
            detection_reason=reason,
            fallback_applied=fallback,
            recovery_output=recovery_output,
            confidence_penalty=confidence_penalty,
            requires_human_review=False
        )


class FailureStateOrchestrator:
    """Runs all failure checks in sequence."""
    
    def __init__(self):
        self.handler = FailureStateHandler()
        
    def analyze_scenario(self, state_params: dict, scenario_data: dict) -> List[FailureResult]:
        """
        Runs all 5 failure case checks on the current state.
        state_params expects:
        - log_content
        - ui_page, visible_fields, user_action
        - browser, os, erp_version, db_version
        - top_cases
        - best_score
        """
        results = []
        
        # Case 1
        res1 = self.handler.handle_missing_logs(
            state_params.get('log_content'), 
            scenario_data
        )
        scenario_data = res1.recovery_output
        results.append(res1)
        
        # Case 2
        res2 = self.handler.handle_corrupted_screenshot(
            state_params.get('ui_page', ''),
            state_params.get('visible_fields', ''),
            state_params.get('user_action', ''),
            scenario_data
        )
        scenario_data = res2.recovery_output
        results.append(res2)
        
        # Case 3
        res3 = self.handler.handle_contradictory_env(
            state_params.get('browser', ''),
            state_params.get('os', ''),
            state_params.get('erp_version', ''),
            state_params.get('db_version', ''),
            scenario_data
        )
        scenario_data = res3.recovery_output
        results.append(res3)
        
        # Case 4
        res4 = self.handler.handle_multiple_root_causes(
            state_params.get('top_cases', []),
            scenario_data
        )
        scenario_data = res4.recovery_output
        results.append(res4)
        
        # Case 5
        res5 = self.handler.handle_no_historical_match(
            state_params.get('best_score', 1.0),
            scenario_data
        )
        scenario_data = res5.recovery_output
        results.append(res5)
        
        return results

if __name__ == "__main__":
    # Test Orcherstrator
    orchestrator = FailureStateOrchestrator()
    sample_state = {
        'log_content': 'NO_LOG_AVAILABLE',
        'ui_page': 'UNKNOWN',
        'visible_fields': 'UNKNOWN',
        'user_action': 'UNKNOWN',
        'browser': 'Safari',
        'os': 'Windows 10',
        'erp_version': 'v13.x',
        'db_version': 'Oracle 19c',
        'top_cases': [
            {'score': 0.88, 'fix_category': 'Config'},
            {'score': 0.85, 'fix_category': 'Database'}
        ],
        'best_score': 0.30
    }
    
    base_scenario = {'title': 'Invoice Bug', 'confidence_score': 0.9}
    
    results = orchestrator.analyze_scenario(sample_state, base_scenario)
    for r in results:
        if r.detected:
            print(f"Detected {r.failure_type}: {r.detection_reason}")
            print(f"Fallback: {r.fallback_applied}")
            print(f"Requires Review: {r.requires_human_review}\n")
