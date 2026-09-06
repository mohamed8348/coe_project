-- schema.sql
-- ERP Bug-Reproduction Assistant Database Schema

CREATE TYPE severity_enum AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW');
CREATE TYPE priority_enum AS ENUM ('P1', 'P2', 'P3', 'P4');
CREATE TYPE decision_enum AS ENUM ('APPROVED', 'REJECTED', 'OVERRIDDEN');
CREATE TYPE risk_level_enum AS ENUM ('HIGH', 'MEDIUM', 'LOW');
CREATE TYPE status_enum AS ENUM ('NEW', 'TRIAGED', 'IN_PROGRESS', 'RESOLVED', 'CLOSED');

CREATE TABLE bugs (
    bug_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    severity severity_enum NOT NULL,
    priority priority_enum NOT NULL,
    module VARCHAR(100) NOT NULL,
    reporter_role VARCHAR(100),
    report_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    os VARCHAR(50),
    browser VARCHAR(50),
    erp_version VARCHAR(50),
    db_version VARCHAR(50),
    region VARCHAR(50),
    timezone VARCHAR(50),
    status status_enum DEFAULT 'NEW'
);

CREATE INDEX idx_bugs_module ON bugs(module);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_status ON bugs(status);

CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    bug_id VARCHAR(50) REFERENCES bugs(bug_id) ON DELETE CASCADE,
    log_content TEXT NOT NULL,
    log_timestamp TIMESTAMP WITH TIME ZONE
);

CREATE TABLE screenshots (
    screenshot_id SERIAL PRIMARY KEY,
    bug_id VARCHAR(50) REFERENCES bugs(bug_id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    metadata JSONB
);

CREATE TABLE resolutions (
    resolution_id SERIAL PRIMARY KEY,
    bug_id VARCHAR(50) REFERENCES bugs(bug_id) ON DELETE CASCADE,
    resolution_text TEXT,
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE scenarios (
    scenario_id VARCHAR(50) PRIMARY KEY,
    bug_id VARCHAR(50) REFERENCES bugs(bug_id) ON DELETE CASCADE,
    generated_steps JSONB NOT NULL,
    expected_result TEXT,
    actual_result TEXT,
    confidence_score NUMERIC(4,3),
    risk_level risk_level_enum,
    requires_approval BOOLEAN DEFAULT FALSE,
    gherkin TEXT,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE approvals (
    approval_id VARCHAR(50) PRIMARY KEY,
    scenario_id VARCHAR(50) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    bug_id VARCHAR(50) REFERENCES bugs(bug_id) ON DELETE CASCADE,
    decision decision_enum NOT NULL,
    decided_by VARCHAR(100) NOT NULL,
    override_reason TEXT,
    decided_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evaluation_runs (
    run_id SERIAL PRIMARY KEY,
    run_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    model_version VARCHAR(50),
    dataset_size INT
);

CREATE TABLE evaluation_metrics (
    metric_id SERIAL PRIMARY KEY,
    run_id INT REFERENCES evaluation_runs(run_id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(10,4) NOT NULL
);

CREATE TABLE chaos_events (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    description TEXT,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);
