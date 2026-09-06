# Deployment Checklist

## Infrastructure Requirements
- [ ] Python 3.11+
- [ ] Docker & Docker Compose
- [ ] PostgreSQL 15 (with pgvector extension)
- [ ] FAISS index storage volume allocated
- [ ] Minimum 16GB RAM for Vector Search & API processing

## Pre-Deployment Checks
- [ ] All unit and integration tests passing (`pytest`)
- [ ] Database schema migrations tested
- [ ] Environment variables configured (`.env`)
- [ ] Synthetic dataset successfully ingested for baseline metrics
- [ ] Evaluator script confirms KPI baselines met

## Security Checklist
- [ ] Role-Based Access Control (RBAC) enforced on `/api/approvals` endpoints
- [ ] Encryption at Rest enabled for PostgreSQL
- [ ] Encryption in Transit (TLS/SSL) configured for FastAPI
- [ ] API Rate limiting configured
- [ ] Audit logging enabled for all `POST` and `PUT` requests

## Monitoring Setup
- [ ] Prometheus metrics endpoint exposed (`/metrics`)
- [ ] Grafana dashboard imported
- [ ] Alerting thresholds set for:
  - 500 Error Rate > 1%
  - Average Latency > 2 seconds
  - System CPU > 80%
- [ ] Health check endpoint (`/health`) configured in load balancer

## Rollback Plan
- [ ] Database snapshot taken before migration
- [ ] Previous Docker image tagged and available
- [ ] Documented procedure for restoring FAISS index from backup
