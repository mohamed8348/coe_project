# Automated Bug-Reproduction Assistant for ERP Systems

> **35% Implementation** — Dataset Generation · Cleaning Pipeline · Baseline System · Prototype Architecture · Evaluation Framework

---

## 🧩 Project Overview

An ERP system spans thousands of tightly coupled business rules across Finance, HR, Payroll, Procurement, Inventory, Manufacturing, CRM, Sales, and Compliance. Bug reports frequently arrive with vague descriptions, missing logs, and contradictory details.

This project builds an **Automated Bug-Reproduction Assistant** that converts raw, incomplete bug reports into executable, reproducible test scenarios using:
- Retrieval-Augmented Generation (RAG) over historical bug resolutions
- Semantic search via FAISS + Sentence Transformers
- Rule-based and ML-based scenario generation
- Explainable AI with confidence scoring
- Human-in-the-loop approval for high-risk actions

---

## 📁 Project Structure

```
coe project/
│
├── data/
│   ├── raw/                    # Synthetic dataset CSVs (generated)
│   └── cleaned/                # Post-cleaning CSVs
│
├── src/
│   ├── dataset_generator/      # Part 1 — 10,000 synthetic ERP bug records
│   ├── cleaning_pipeline/      # Part 2 — NLP cleaning + deduplication
│   ├── baseline/               # Part 3 — Rule-based keyword baseline
│   ├── assistant/              # Part 4 — Core RAG pipeline
│   ├── explainability/         # Part 5 — Evidence blocks + confidence
│   ├── human_in_loop/          # Part 6 — Approval workflow
│   ├── failure_states/         # Part 7 — 5 failure-case handlers
│   ├── chaos_testing/          # Part 8 — Event chaos simulation
│   ├── test_generation/        # Part 9 — Gherkin/Selenium/Playwright/Postman
│   └── evaluation/             # Parts 10-12 — Metrics + error analysis
│
├── api/                        # FastAPI REST API
│   ├── main.py
│   ├── schemas.py
│   └── routers/
│       ├── bugs.py
│       ├── scenarios.py
│       └── approvals.py
│
├── db/
│   └── schema.sql              # PostgreSQL schema
│
├── reports/
│   ├── kpi_table.md
│   ├── error_analysis.md
│   ├── stakeholder_validation.md
│   ├── ethics_governance.md
│   └── deployment_checklist.md
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Download NLTK data (first time only):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('stopwords')"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Generate the Synthetic Dataset (Part 1)

```bash
python src/dataset_generator/generate_dataset.py --num-records 10000 --seed 42
```

Output: `data/raw/bugs_raw.csv`, `data/raw/logs_raw.csv`, `data/raw/screenshots_raw.csv`, `data/raw/resolutions_raw.csv`

### 4. Run the Cleaning Pipeline (Part 2)

```bash
python src/cleaning_pipeline/clean_pipeline.py
```

Output: `data/cleaned/bugs_cleaned.csv` (and related files)

### 5. Run Baseline Evaluation (Part 3)

```bash
python src/baseline/baseline_system.py
```

Output: `data/baseline_results.csv` + metrics printed to console

### 6. Run the Full Evaluation (Parts 10–12)

```bash
python src/evaluation/evaluator.py
```

### 7. Start the API Server

```bash
uvicorn api.main:app --reload --port 8000
```

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 8. Run with Docker

```bash
docker-compose -f docker/docker-compose.yml up --build
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/bugs/ingest` | Ingest a bug report → generate scenario |
| `GET` | `/api/bugs/{bug_id}` | Retrieve bug details |
| `GET` | `/api/scenarios/{scenario_id}` | Get generated scenario |
| `GET` | `/api/scenarios/{scenario_id}/explanation` | Get explainability evidence |
| `GET` | `/api/scenarios/{scenario_id}/tests` | Get Gherkin/Selenium/Playwright/Postman |
| `GET` | `/api/approvals/pending` | List pending human approvals |
| `POST` | `/api/approvals/{id}/decide` | Submit approval decision |
| `GET` | `/api/evaluation/report` | Get evaluation metrics |

---

## 📊 KPI Targets

| Metric | Baseline | Target |
|--------|----------|--------|
| Reproduction Success Rate | 23% | 75% |
| Mean Triage Time | 45 min | 8 min |
| Scenario Generation F1 | 0.20 | 0.70 |
| Failure Recovery Rate | 0% | 85% |

See [`reports/kpi_table.md`](reports/kpi_table.md) for full details.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| API | FastAPI + Uvicorn |
| Embeddings | Sentence-Transformers (all-MiniLM-L6-v2) |
| Vector Search | FAISS |
| NLP | NLTK + Scikit-learn |
| Database | PostgreSQL 15 + pgvector |
| Containerization | Docker + Docker Compose |
| Test Generation | Selenium · Playwright · Postman |
| Evaluation | Scikit-learn metrics |

---

## 📋 Parts Implemented

| Part | Description | Status |
|------|-------------|--------|
| 1 | Synthetic Dataset Generation (10,000 records) | ✅ |
| 2 | Data Cleaning Pipeline | ✅ |
| 3 | Rule-Based Baseline | ✅ |
| 4 | Core Assistant Pipeline (RAG) | ✅ |
| 5 | Recommendation Explainability | ✅ |
| 6 | Human-in-the-Loop Controls | ✅ |
| 7 | Failure-State Design | ✅ |
| 8 | Event Chaos Testing | ✅ |
| 9 | Executable Scenario Generation | ✅ |
| 10–12 | Evaluation Framework + Error Analysis | ✅ |
| 13 | Stakeholder Validation | ✅ |
| 14 | Ethics & Governance | ✅ |
| 15 | Deployment Checklist | ✅ |

---

## 👥 Stakeholder Validation

See [`reports/stakeholder_validation.md`](reports/stakeholder_validation.md) for the full validation study with QA Engineers, ERP Consultants, and Product Owners.

---

## ⚖️ Ethics & Governance

See [`reports/ethics_governance.md`](reports/ethics_governance.md) for discussion of hallucination risks, bias mitigation, PII handling, and audit trail design.

---

## 📄 License

Academic project — for educational and research purposes.
