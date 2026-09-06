# KPI Measurement Report — ERP Bug-Reproduction Assistant

**Generated:** 2026-09-06 20:38:57
**Baseline results source:** `data/baseline_results.csv`

---

## KPI Table

| Metric | Baseline | Target | Measured | Status |
|--------|----------|--------|----------|--------|
| Reproduction Success Rate (RSR) | 23.00% | 75.00% | 0.00% | 🔴 |
| Mean Triage Time (min) | 45.0 | 8.0 | TBD | ⏳ |
| Scenario Generation Accuracy | 18.00% | 70.00% | 0.00% | 🔴 |
| Precision | 21.00% | 72.00% | 13.82% | 🔴 |
| Recall | 19.00% | 68.00% | 18.93% | 🔴 |
| F1 Score | 20.00% | 70.00% | 15.64% | 🔴 |
| Scenario Completeness Score | 35.00% | 80.00% | TBD | ⏳ |
| Human Approval Rate (%) | N/A | 15.00% | TBD | ⏳ |
| Failure Recovery Rate | 0.00% | 85.00% | TBD | ⏳ |
| Time Saved per Bug (hrs) | 0.00% | 60.00% | 69.00% | ✅ |

> ✅ = Target met | 🟡 = Within 70% of target | 🔴 = Below threshold | ⏳ = Not yet measured

---

### Dataset Statistics

- **Raw records generated:** 10,000
- **Records after cleaning:** 10,000
- **Missing logs (raw):** 0
- **Missing screenshots (raw):** 0
- **Semantic duplicates flagged:** 154

**Module Distribution:**
  - CRM: 1,096 records
  - Compliance: 1,083 records
  - Finance: 1,096 records
  - HR: 1,178 records
  - Inventory: 1,124 records
  - Manufacturing: 1,121 records
  - Payroll: 1,156 records
  - Procurement: 1,058 records
  - Sales: 1,088 records

---

### Time Savings Estimate (on 1,500 evaluated bugs)
| Item | Value |
|------|-------|
| Manual triage time (total) | 1,125.0 hrs |
| Automated pipeline time (total) | 87.5 hrs |
| **Hours saved** | **1,037.5 hrs** |
| **Percent saved** | **92.2%** |
| Time saved per bug | 0.69 hrs |

---

## Legend

| Metric | Definition |
|--------|-----------|
| RSR | Fraction of bugs where generated scenario F1 > 0.5 |
| Precision | TP / (TP + FP) at word-level step comparison |
| Recall | TP / (TP + FN) at word-level step comparison |
| F1 Score | Harmonic mean of Precision and Recall |
| Scenario Completeness | Fraction of required fields populated |
| Human Approval Rate | % of HIGH/CRITICAL scenarios needing human sign-off |
| Failure Recovery Rate | % of failure-state cases successfully recovered |
| Time Saved / Bug | (Manual triage − Automated pipeline) per bug |
