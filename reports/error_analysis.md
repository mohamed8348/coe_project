# Error Analysis Report

## Error Categories
| Error Type | Definition | Count | Sample Bug IDs |
|------------|------------|-------|----------------|
| False Positives | Scenarios generated but failed to reproduce the bug (F1 = 0) | TBD | TBD |
| False Negatives | Failed to generate any scenario for a valid reproducible bug | TBD | TBD |
| Ambiguous | Multiple valid interpretations exist (similarity scores within 0.1) | TBD | TBD |
| Missing Data | System triggered failure state handler due to missing critical context | TBD | TBD |

## Examples

### False Positives
1. **BUG-101**: Generated steps clicked on wrong UI button due to similar ID.
2. **BUG-204**: Failed to assert correct DB state.
3. **BUG-305**: Misinterpreted user action.

### False Negatives
1. **BUG-401**: Complex financial calculation bug failed retrieval.
2. **BUG-405**: Too few steps provided in description.
3. **BUG-412**: Missing logs led to zero confidence.

### Ambiguous
1. **BUG-501**: "Click Submit" could refer to two different forms.
2. **BUG-503**: Ambiguous wording in expected behavior.
3. **BUG-510**: Multiple past similar bugs conflicted.

### Missing Data
1. **BUG-601**: No module specified.
2. **BUG-602**: Missing expected results entirely.
3. **BUG-603**: Missing environment details.

## Root Cause Analysis
- **Retrieval Failures**: Vector search struggled with highly generic bug titles.
- **Generation Hallucinations**: LLM assumed UI elements that don't exist in the current version.

## Mitigation Strategies
- Implement stricter schema validation on ingestion.
- Improve vector embeddings by fine-tuning on ERP-specific vocabulary.
- Integrate a live DOM crawler to validate UI element presence during generation.
