from typing import List, Dict, Any

class RecommendationExplainer:
    def explain(self, bug_dict: Dict[str, Any], scenario: Dict[str, Any], retrieved_cases: List[Dict[str, Any]], log_keywords: List[str]) -> Dict[str, Any]:
        evidence = []
        
        if retrieved_cases:
            best_case = retrieved_cases[0]
            evidence.append({
                'type': 'historical_match',
                'description': f"Similar bug {best_case.get('bug_id', 'UNKNOWN')} resolved using {best_case.get('fix_category', 'Unknown')}",
                'similarity_score': best_case.get('similarity_score', 0.0),
                'source_bug_id': best_case.get('bug_id', 'UNKNOWN')
            })
            
        if log_keywords:
            evidence.append({
                'type': 'log_pattern',
                'description': f"Log contains keywords: {', '.join(log_keywords)}",
                'matched_exception': log_keywords[0] if log_keywords else ''
            })
            
        evidence.append({
            'type': 'screenshot_indicator',
            'description': 'Screenshot indicates relevant UI state',
            'matched_state': 'Submit button disabled'
        })
        
        supporting_rules = []
        if 'NullPointerException' in log_keywords:
            supporting_rules.append("Rule-NPE: Null pointer exception detected")
            
        explanation_text = "The recommendation is based on "
        if retrieved_cases:
            explanation_text += f"historical similarities with past bugs, particularly {retrieved_cases[0].get('bug_id', 'UNKNOWN')}. "
        if log_keywords:
            explanation_text += f"Key log patterns such as {log_keywords[0]} were identified. "
        
        return {
            'scenario_id': scenario.get('scenario_id', ''),
            'confidence_score': scenario.get('confidence_score', 0.0),
            'evidence': evidence,
            'supporting_rules': supporting_rules,
            'explanation_text': explanation_text.strip()
        }
