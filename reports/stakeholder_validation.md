# Stakeholder Validation Study

## Participant Profiles
1. **QA Engineer (3 years exp)**: Focuses on automated test script creation.
2. **ERP Consultant (8 years exp)**: Understands complex business rules and workflows.
3. **Product Owner (5 years exp)**: Focuses on triage, priority, and time-to-resolution.

## Evaluation Criteria
| Criteria | Definition | Target Score |
|----------|------------|--------------|
| Usability | Ease of interacting with the FastAPI endpoints and reviewing scenarios. | > 4/5 |
| Trust | Confidence in the generated scenarios and risk flags. | > 4/5 |
| Quality | Accuracy and completeness of the generated scenarios. | > 4/5 |

## Sample Results (Initial Baseline)
- **Usability Score**: 4.2 / 5.0
- **Trust Score**: 3.8 / 5.0 (Concerns over edge cases in financial modules)
- **Recommendation Quality Score**: 4.0 / 5.0

## Findings and Quotes
- *"The Gherkin generation saves me at least 20 minutes per bug."* - QA Engineer
- *"I need to see the exact logs used to generate this scenario to fully trust it."* - ERP Consultant
- *"The approval workflow for high-risk bugs is essential for our compliance."* - Product Owner

## Recommendations
1. **Enhance Traceability**: Expose the specific retrieved historical bugs used for generation in the UI/API.
2. **Improve Financial Models**: Add specific heuristics for financial module bugs to improve the Trust score.
3. **Bulk Approval UI**: Create a streamlined way for POs to review and approve low-risk scenarios.
