import argparse
import random
import json
import os
from datetime import datetime
import pandas as pd
import numpy as np
from faker import Faker

faker = Faker()

MODULES = ["Finance", "HR", "Payroll", "Procurement", "Inventory", "Manufacturing", "CRM", "Sales", "Compliance"]
SEVERITIES = ["Critical", "High", "Medium", "Low"]
PRIORITIES = ["P1", "P2", "P3", "P4"]
ROLES = ["QA Engineer", "Business Analyst", "End User", "Developer", "Manager"]
OS_LIST = ["Windows 10", "Windows 11", "Ubuntu 20.04", "macOS 13"]
BROWSERS = ["Chrome", "Firefox", "Edge", "Safari"]
ERP_VERSIONS = ["v12.1", "v12.2", "v13.0", "v13.1", "v14.0"]
DB_VERSIONS = ["PostgreSQL 13", "PostgreSQL 14", "Oracle 19c", "SQL Server 2019"]
REGIONS = ["US", "EU", "APAC", "MENA", "LATAM"]
TIMEZONES = ["UTC", "UTC+5:30", "UTC+8", "UTC-5", "UTC+1"]
LOG_LEVELS = ["INFO", "WARN", "ERROR", "FATAL"]
FIX_CATEGORIES = ["Code Fix", "Configuration", "Data Patch", "Workflow Reset", "DB Rollback"]

DOMAIN_KNOWLEDGE = {
    "Finance": {
        "entities": ["Invoice", "Ledger", "Payment", "Tax Report", "Reconciliation", "Journal Entry", "Asset"],
        "actions": ["creation fails", "shows incorrect balance", "duplicates entry", "is locked", "times out on save", "calculates wrong tax", "fails to post"],
        "ui_pages": ["Invoice Approval Screen", "General Ledger Dashboard", "Payment Processing", "Tax Setup", "Reconciliation View"],
        "fields": ["amount", "tax_rate", "vendor_id", "date", "status", "account_code"],
        "root_causes": ["Missing null check in approval workflow service", "Precision loss in float division", "Database deadlock during batch update", "Currency conversion rate missing", "API timeout to tax service"],
    },
    "HR": {
        "entities": ["Employee Profile", "Leave Request", "Onboarding Workflow", "Performance Review", "Timesheet", "Benefits Plan", "Offboarding"],
        "actions": ["does not load", "approver is null", "submits twice", "shows wrong manager", "data truncated", "fails to update status", "sends blank email"],
        "ui_pages": ["Employee Directory", "Leave Approval", "Onboarding Checklist", "Performance Review Dashboard", "Timesheet Entry"],
        "fields": ["employee_id", "manager_id", "leave_type", "start_date", "end_date", "department"],
        "root_causes": ["Manager hierarchy cycle detected", "Stale cache in profile service", "Email queue worker crashed", "Missing role permission", "Invalid date format parsed"],
    },
    "Payroll": {
        "entities": ["Payslip", "Salary Calculation", "Bonus Disbursal", "Tax Deduction", "Direct Deposit", "Overtime Calc", "Final Settlement"],
        "actions": ["shows $0", "deducts twice", "fails to generate pdf", "routing number missing", "calculates incorrect overtime", "mismatched tax bracket", "stuck in processing"],
        "ui_pages": ["Payroll Run Dashboard", "Payslip View", "Tax Deduction Settings", "Bonus Allocation", "Direct Deposit Setup"],
        "fields": ["net_pay", "gross_pay", "tax_amount", "account_number", "routing_number", "bonus_amount"],
        "root_causes": ["Tax table API timeout", "Integer overflow in bonus calculation", "Bank integration endpoint changed", "PDF generator out of memory", "Race condition in batch run"],
    },
    "Procurement": {
        "entities": ["Purchase Order", "Vendor Contract", "RFQ", "Goods Receipt", "Supplier Portal", "Requisition", "Invoice Matching"],
        "actions": ["fails to transition state", "approver list empty", "shows incorrect currency", "duplicate PO generated", "cannot upload attachment", "vendor not found", "price mismatch"],
        "ui_pages": ["PO Creation", "Vendor Onboarding", "RFQ Dashboard", "Goods Receipt Note", "Requisition Approval"],
        "fields": ["po_number", "vendor_name", "total_amount", "currency", "delivery_date", "items_list"],
        "root_causes": ["Vendor sync job failed", "Currency exchange rate stale", "Attachment size limit hardcoded", "State machine configuration error", "Null pointer in routing logic"],
    },
    "Inventory": {
        "entities": ["Stock Level", "Warehouse Transfer", "Barcode Scanner", "Cycle Count", "Batch Expiry", "Reorder Point", "Bin Location"],
        "actions": ["shows negative stock", "transfer stuck", "reads wrong code", "fails to save count", "does not trigger alert", "items missing from view", "location mismatch"],
        "ui_pages": ["Stock Overview", "Transfer Request", "Barcode Entry", "Cycle Count Dashboard", "Reorder Settings"],
        "fields": ["sku", "quantity", "warehouse_id", "bin_id", "batch_number", "expiry_date"],
        "root_causes": ["Race condition in stock decrement", "Deadlock in transfer transaction", "Scanner API schema mismatch", "Async event dropped", "Location ID missing from payload"],
    },
    "Manufacturing": {
        "entities": ["Bill of Materials", "Work Order", "Machine Log", "Quality Check", "Routing Plan", "Scrap Report", "Shift Schedule"],
        "actions": ["cost rolls up incorrectly", "order stuck in pending", "log sync fails", "rejects valid part", "sequence out of order", "calculates wrong yield", "cannot assign operator"],
        "ui_pages": ["BOM Designer", "Work Order Dashboard", "Machine Integration", "Quality Assurance", "Routing Setup"],
        "fields": ["bom_id", "work_order_id", "machine_id", "operator_id", "yield_rate", "scrap_reason"],
        "root_causes": ["Circular dependency in BOM", "Machine IoT gateway timeout", "Operator certification expired check failed", "Yield calculation divide by zero", "Shift timing off by one hour"],
    },
    "CRM": {
        "entities": ["Customer Profile", "Lead Record", "Opportunity", "Contact Note", "Campaign", "Quote", "Support Ticket"],
        "actions": ["merges incorrectly", "assignment rules fail", "stage not updating", "note fails to save", "email bounce not logged", "quote calculation wrong", "SLA timer reset"],
        "ui_pages": ["Customer 360", "Lead Kanban", "Opportunity Details", "Campaign Manager", "Quote Builder"],
        "fields": ["customer_id", "lead_score", "opportunity_stage", "contact_email", "campaign_budget", "quote_total"],
        "root_causes": ["Race condition in lead assignment", "Salesforce API rate limit exceeded", "Notes field character encoding issue", "SLA timezone conversion error", "Missing mapping in merge job"],
    },
    "Sales": {
        "entities": ["Sales Order", "Pricing Discount", "Commission", "Territory Plan", "Sales Forecast", "Contract", "Delivery Schedule"],
        "actions": ["applies wrong discount", "fails credit check", "commission calculates as 0", "territory unassigned", "forecast roll-up fails", "signature missing", "schedule overlaps"],
        "ui_pages": ["Sales Order Entry", "Discount Matrix", "Commission Dashboard", "Territory Manager", "Forecast View"],
        "fields": ["order_id", "discount_percentage", "sales_rep", "territory_id", "forecast_amount", "contract_status"],
        "root_causes": ["Discount priority rule clash", "Credit API unresponsive", "Commission logic date boundary bug", "Territory tree traversal error", "Signature webhook dropped"],
    },
    "Compliance": {
        "entities": ["Audit Log", "GDPR Request", "Risk Assessment", "Policy Document", "Access Review", "Compliance Report", "Data Retention"],
        "actions": ["fails to export", "anonymization incomplete", "assessment score wrong", "cannot upload pdf", "review chain broken", "report missing columns", "purge job fails"],
        "ui_pages": ["Audit Trail", "Data Privacy Request", "Risk Matrix", "Policy Repository", "Access Certification"],
        "fields": ["audit_id", "request_type", "risk_score", "policy_version", "reviewer_id", "retention_period"],
        "root_causes": ["Export builder memory leak", "PII regex missed phone numbers", "Review workflow state corrupted", "S3 bucket permission denied", "Cron job overlap for purging"],
    }
}

def generate_bug_reports(num_records, seed):
    random.seed(seed)
    np.random.seed(seed)
    faker.seed_instance(seed)
    
    bugs = []
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for _ in range(num_records):
        module = random.choice(MODULES)
        dk = DOMAIN_KNOWLEDGE[module]
        
        entity = random.choice(dk["entities"])
        action = random.choice(dk["actions"])
        
        title = f"{entity} {action} when {faker.bs()}"
        description = f"Users are reporting that the {entity.lower()} {action}. Expected normal behavior but it failed. Happens intermittently. {faker.sentence()}"
        
        ui_page = random.choice(dk["ui_pages"])
        visible_fields = ",".join(random.sample(dk["fields"], k=random.randint(2, len(dk["fields"]))))
        user_action = f"Clicked {random.choice(['Submit', 'Save', 'Approve', 'Delete', 'Calculate', 'Export'])} button"
        expected_behavior = f"{entity} is processed successfully."
        actual_behavior = f"{entity} {action}."
        
        root_cause = random.choice(dk["root_causes"])
        fix_category = random.choice(FIX_CATEGORIES)
        workaround = f"Manually update via {random.choice(['DB', 'Admin Panel', 'API'])}."
        final_resolution = f"Implemented fix for {root_cause.lower()}. Added unit tests. Verified in staging."
        
        reproducible_steps = [
            f"Login as {random.choice(ROLES)}",
            f"Navigate to {module} > {ui_page}",
            user_action,
            "Observe error"
        ]
        
        log_level = random.choice(LOG_LEVELS)
        log_content = ""
        if random.random() > 0.15: # 15% missing logs
            log_content = f"[{log_level}] {faker.date_time_between(start_date=start_date, end_date=end_date).isoformat()} - Error in {entity.replace(' ', '')}Service\n"
            log_content += f"Caused by: {root_cause}\n"
            log_content += f"Stack trace:\n  at {module.lower()}.services.{entity.replace(' ', '')}Service.process(Line {random.randint(10, 500)})\n"
            log_content += f"  at {module.lower()}.controllers.{entity.replace(' ', '')}Controller.handle(Line {random.randint(10, 100)})"
        
        screenshot_data = {}
        if random.random() > 0.10: # 10% missing screenshot metadata
            screenshot_data = {
                "ui_page": ui_page,
                "visible_fields": visible_fields,
                "user_action": user_action,
                "expected_behavior": expected_behavior,
                "actual_behavior": actual_behavior
            }
        else:
            screenshot_data = {
                "ui_page": "",
                "visible_fields": "",
                "user_action": "",
                "expected_behavior": "",
                "actual_behavior": ""
            }
            
        bug_record = {
            "title": title,
            "description": description,
            "severity": random.choice(SEVERITIES),
            "priority": random.choice(PRIORITIES),
            "module": module,
            "reporter_role": random.choice(ROLES),
            "report_date": faker.date_time_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d'),
            
            "os": random.choice(OS_LIST),
            "browser": random.choice(BROWSERS),
            "erp_version": random.choice(ERP_VERSIONS),
            "db_version": random.choice(DB_VERSIONS),
            "region": random.choice(REGIONS),
            "timezone": random.choice(TIMEZONES),
            
            "log_level": log_level,
            "log_content": log_content,
            
            "ui_page": screenshot_data["ui_page"],
            "visible_fields": screenshot_data["visible_fields"],
            "user_action": screenshot_data["user_action"],
            "expected_behavior": screenshot_data["expected_behavior"],
            "actual_behavior": screenshot_data["actual_behavior"],
            
            "root_cause": root_cause,
            "fix_category": fix_category,
            "workaround": workaround,
            "final_resolution": final_resolution,
            
            "reproducible_steps": json.dumps(reproducible_steps),
            "expected_result": expected_behavior,
            "actual_result": actual_behavior,
            "executable_test_case": f"Feature: Fix {entity} issue\n  Scenario: Verify {entity} {action.split()[0]}\n    Given user is on {ui_page}\n    When they click {user_action.split()[1]}\n    Then {expected_behavior.lower()}"
        }
        bugs.append(bug_record)
        
    return bugs

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ERP bug dataset")
    parser.add_argument("--output-dir", default="data/raw", help="Output directory")
    parser.add_argument("--num-records", type=int, default=10000, help="Number of records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    
    print(f"Generating {args.num_records} bug records...")
    
    unique_count = int(args.num_records * 0.95)
    dup_count = args.num_records - unique_count
    
    bugs = generate_bug_reports(unique_count, args.seed)
    
    random.seed(args.seed + 1)
    indices_to_duplicate = random.choices(range(len(bugs)), k=dup_count)
    
    for idx in indices_to_duplicate:
        dup = dict(bugs[idx])
        dup["description"] += " (Duplicate report: " + faker.word() + ")"
        bugs.append(dup)
        
    random.shuffle(bugs)
    
    # Assign IDs
    for i, bug in enumerate(bugs):
        bug["bug_id"] = f"BUG-{i+1:05d}"
        
    df = pd.DataFrame(bugs)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    df.to_csv(os.path.join(args.output_dir, "bugs_raw.csv"), index=False)
    df[["bug_id", "log_level", "log_content"]].to_csv(os.path.join(args.output_dir, "logs_raw.csv"), index=False)
    df[["bug_id", "ui_page", "visible_fields", "user_action", "expected_behavior", "actual_behavior"]].to_csv(os.path.join(args.output_dir, "screenshots_raw.csv"), index=False)
    df[["bug_id", "root_cause", "fix_category", "workaround", "final_resolution", "reproducible_steps", "expected_result", "actual_result", "executable_test_case"]].to_csv(os.path.join(args.output_dir, "resolutions_raw.csv"), index=False)
    
    print("Generation complete!")
    print(f"Total records: {len(df)}")
    print(f"Missing logs: {len(df[df['log_content'] == ''])}")
    print(f"Missing screenshots: {len(df[df['ui_page'] == ''])}")
    print(f"Output directory: {args.output_dir}")

if __name__ == "__main__":
    main()
