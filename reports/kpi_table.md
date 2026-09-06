# KPI Table — ERP Bug-Reproduction Assistant

| Metric | Baseline | Target | Measured |
|--------|----------|--------|----------|
| Reproduction Success Rate (RSR) | 23% | 75% | TBD |
| Mean Triage Time (minutes) | 45 min | 8 min | TBD |
| Scenario Generation Accuracy | 18% | 70% | TBD |
| Human Approval Rate | N/A | <15% | TBD |
| Failure Recovery Rate | 0% | 85% | TBD |
| Precision | 0.21 | 0.72 | TBD |
| Recall | 0.19 | 0.68 | TBD |
| F1 Score | 0.20 | 0.70 | TBD |
| Scenario Completeness Score | 0.35 | 0.80 | TBD |
| Time Saved per Bug (hours) | 0 | 0.6 hrs | TBD |

## Explanations

- **Reproduction Success Rate (RSR)**: The percentage of generated test scenarios that successfully reproduce the bug in a local/staging environment.
- **Mean Triage Time**: Average time spent analyzing a bug before starting reproduction efforts.
- **Scenario Generation Accuracy**: Percentage of scenarios perfectly matching ground truth without human editing.
- **Human Approval Rate**: Percentage of scenarios flagged as high-risk requiring human override or approval.
- **Failure Recovery Rate**: The system's ability to gracefully handle missing data and continue with partial generation.
- **Precision, Recall, F1 Score**: Standard NLP/retrieval metrics applied to the generated steps vs ground truth steps.
- **Scenario Completeness Score**: Metric indicating how many required scenario fields (context, steps, assertions) are adequately filled.
- **Time Saved per Bug**: Estimated total hours saved by automating triage and reproduction tasks.
