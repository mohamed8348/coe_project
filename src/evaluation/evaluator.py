import pandas as pd
from typing import Tuple, Dict, List, Any
import json
import logging
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

class Evaluator:
    def __init__(self):
        pass

    def split_dataset(self, df: pd.DataFrame, train: float = 0.70, val: float = 0.15, test: float = 0.15, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Splits the dataset into train, validation, and test sets, stratified by module."""
        # Check if module exists for stratification
        stratify_col = df['module'] if 'module' in df.columns else None
        
        train_df, temp_df = train_test_split(
            df, 
            test_size=(val + test), 
            random_state=seed, 
            stratify=stratify_col
        )
        
        stratify_temp = temp_df['module'] if 'module' in temp_df.columns else None
        
        # Calculate proportion of validation set relative to the temp set
        val_ratio = val / (val + test)
        
        val_df, test_df = train_test_split(
            temp_df, 
            test_size=(1 - val_ratio), 
            random_state=seed, 
            stratify=stratify_temp
        )
        
        return train_df, val_df, test_df

    def step_precision(self, predicted_steps: List[str], true_steps: List[str]) -> float:
        if not predicted_steps:
            return 0.0
        # Simple string matching for demonstration (in reality, semantic matching)
        correct = sum(1 for step in predicted_steps if step in true_steps)
        return correct / len(predicted_steps)

    def step_recall(self, predicted_steps: List[str], true_steps: List[str]) -> float:
        if not true_steps:
            return 1.0 if not predicted_steps else 0.0
        correct = sum(1 for step in predicted_steps if step in true_steps)
        return correct / len(true_steps)

    def step_f1(self, predicted_steps: List[str], true_steps: List[str]) -> float:
        p = self.step_precision(predicted_steps, true_steps)
        r = self.step_recall(predicted_steps, true_steps)
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)

    def reproduction_success_rate(self, predictions: List[Dict], ground_truth: List[Dict]) -> float:
        """Calculates fraction of scenarios where step-level F1 > 0.5."""
        if not predictions or not ground_truth or len(predictions) != len(ground_truth):
            return 0.0
            
        successes = 0
        for p, t in zip(predictions, ground_truth):
            pred_steps = p.get('generated_steps', [])
            true_steps = t.get('steps', [])
            f1 = self.step_f1(pred_steps, true_steps)
            if f1 > 0.5:
                successes += 1
                
        return successes / len(predictions)

    def scenario_completeness(self, scenario: dict) -> float:
        """Returns score 0-1 based on how many required fields are populated."""
        required_fields = ['scenario_id', 'bug_id', 'module', 'generated_steps', 'expected_result', 'actual_result', 'confidence_score']
        if not required_fields:
            return 0.0
        populated = sum(1 for f in required_fields if scenario.get(f) is not None and scenario.get(f) != "")
        return populated / len(required_fields)

    def time_saved_estimate(self, n_bugs: int, avg_manual_minutes: float = 45.0, avg_auto_minutes: float = 3.5) -> dict:
        total_manual_hours = (n_bugs * avg_manual_minutes) / 60
        total_auto_hours = (n_bugs * avg_auto_minutes) / 60
        hours_saved = total_manual_hours - total_auto_hours
        percent_saved = (hours_saved / total_manual_hours) * 100 if total_manual_hours > 0 else 0
        
        return {
            'total_manual_hours': total_manual_hours,
            'total_auto_hours': total_auto_hours,
            'hours_saved': hours_saved,
            'percent_saved': percent_saved
        }

    def analyze_errors(self, predictions: List[Dict], ground_truth: List[Dict]) -> dict:
        """Categorize and count errors based on evaluation."""
        analysis = {
            'false_positives': {'count': 0, 'examples': [], 'bug_ids': []},
            'false_negatives': {'count': 0, 'examples': [], 'bug_ids': []},
            'ambiguous': {'count': 0, 'examples': [], 'bug_ids': []},
            'missing_data_failures': {'count': 0, 'examples': [], 'bug_ids': []}
        }
        
        for p, t in zip(predictions, ground_truth):
            bug_id = p.get('bug_id')
            pred_steps = p.get('generated_steps', [])
            true_steps = t.get('steps', [])
            
            # Missing Data Failures
            if not p.get('module') or not p.get('expected_result'):
                analysis['missing_data_failures']['count'] += 1
                analysis['missing_data_failures']['bug_ids'].append(bug_id)
                if len(analysis['missing_data_failures']['examples']) < 3:
                    analysis['missing_data_failures']['examples'].append(p)
                continue
                
            # False Negative: failed to generate any steps
            if not pred_steps and true_steps:
                analysis['false_negatives']['count'] += 1
                analysis['false_negatives']['bug_ids'].append(bug_id)
                if len(analysis['false_negatives']['examples']) < 3:
                    analysis['false_negatives']['examples'].append(p)
                continue
                
            # False Positive: generated steps but F1 is 0
            f1 = self.step_f1(pred_steps, true_steps)
            if pred_steps and f1 == 0:
                analysis['false_positives']['count'] += 1
                analysis['false_positives']['bug_ids'].append(bug_id)
                if len(analysis['false_positives']['examples']) < 3:
                    analysis['false_positives']['examples'].append(p)
                continue
                
            # Ambiguous (mock implementation - assuming confidence_score reflects ambiguity if low)
            if p.get('confidence_score', 1.0) < 0.6:
                analysis['ambiguous']['count'] += 1
                analysis['ambiguous']['bug_ids'].append(bug_id)
                if len(analysis['ambiguous']['examples']) < 3:
                    analysis['ambiguous']['examples'].append(p)
                    
        return analysis

    def generate_report(self, results: dict, output_path: str):
        """Generates a markdown report."""
        report = f"# Evaluation Report\n\n"
        report += f"## Metrics\n"
        report += f"- Reproduction Success Rate: {results.get('rsr', 0):.2f}\n"
        report += f"- Precision: {results.get('precision', 0):.2f}\n"
        report += f"- Recall: {results.get('recall', 0):.2f}\n"
        report += f"- F1 Score: {results.get('f1', 0):.2f}\n"
        report += f"- Scenario Completeness: {results.get('completeness', 0):.2f}\n"
        
        ts = results.get('time_saved', {})
        report += f"## Time Savings\n"
        report += f"- Manual Hours: {ts.get('total_manual_hours', 0):.2f}\n"
        report += f"- Automated Hours: {ts.get('total_auto_hours', 0):.2f}\n"
        report += f"- Hours Saved: {ts.get('hours_saved', 0):.2f} ({ts.get('percent_saved', 0):.2f}%)\n"
        
        err = results.get('error_analysis', {})
        report += f"## Error Analysis\n"
        report += f"| Error Type | Count | Sample Bug IDs |\n"
        report += f"|------------|-------|----------------|\n"
        report += f"| False Positives | {err.get('false_positives', {}).get('count', 0)} | {', '.join(err.get('false_positives', {}).get('bug_ids', [])[:3])} |\n"
        report += f"| False Negatives | {err.get('false_negatives', {}).get('count', 0)} | {', '.join(err.get('false_negatives', {}).get('bug_ids', [])[:3])} |\n"
        report += f"| Ambiguous | {err.get('ambiguous', {}).get('count', 0)} | {', '.join(err.get('ambiguous', {}).get('bug_ids', [])[:3])} |\n"
        report += f"| Missing Data | {err.get('missing_data_failures', {}).get('count', 0)} | {', '.join(err.get('missing_data_failures', {}).get('bug_ids', [])[:3])} |\n"
        
        with open(output_path, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to {output_path}")

if __name__ == '__main__':
    # Main run mock
    print("Running evaluation baseline...")
    evaluator = Evaluator()
    # Mock data
    preds = [{'bug_id': '1', 'module': 'HR', 'generated_steps': ['login', 'click HR'], 'expected_result': 'page loads', 'confidence_score': 0.9}]
    truth = [{'bug_id': '1', 'steps': ['login', 'click HR', 'click payroll']}]
    rsr = evaluator.reproduction_success_rate(preds, truth)
    print(f"RSR: {rsr}")
