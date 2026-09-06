import os
import argparse
import pandas as pd
import json

TAXONOMY = {
    'Finance': ['invoice', 'payment', 'ledger', 'journal', 'tax', 'reconciliation', 'approval', 'voucher'],
    'HR': ['employee', 'leave', 'attendance', 'appraisal', 'recruitment', 'onboarding', 'termination'],
    'Payroll': ['salary', 'payslip', 'deduction', 'bonus', 'tax', 'overtime', 'pf', 'esi'],
    'Procurement': ['purchase order', 'vendor', 'rfq', 'goods receipt', 'three-way match', 'po approval'],
    'Inventory': ['stock', 'warehouse', 'reorder', 'transfer', 'lot', 'serial', 'bin', 'valuation'],
    'Manufacturing': ['bom', 'work order', 'routing', 'production', 'scrap', 'quality', 'mrp'],
    'CRM': ['lead', 'opportunity', 'contact', 'pipeline', 'follow-up', 'quote', 'campaign'],
    'Sales': ['sales order', 'quotation', 'delivery', 'invoice', 'credit note', 'discount', 'commission'],
    'Compliance': ['audit', 'gdpr', 'sox', 'policy', 'regulation', 'report', 'control', 'risk']
}

TEMPLATES = {
    # Finance
    'finance_invoice_approval': {
        'keywords': ['invoice', 'approval', 'submit'],
        'steps': [
            'Navigate to Finance > Accounts Payable > Invoices',
            'Open invoice record with status Pending Approval',
            'Click the Submit for Approval button',
            'Verify approval workflow is triggered',
            'Check invoice status changes to Approved'
        ]
    },
    'finance_payment_reconciliation': {
        'keywords': ['payment', 'reconciliation', 'ledger'],
        'steps': [
            'Navigate to Finance > Bank > Reconciliation',
            'Select bank account and date range',
            'Click Auto-Match Transactions',
            'Verify unmatched items',
            'Post reconciliation'
        ]
    },
    'finance_journal_entry': {
        'keywords': ['journal', 'ledger', 'voucher'],
        'steps': [
            'Navigate to Finance > General Ledger > Journal Entries',
            'Create new journal entry',
            'Add debit and credit lines',
            'Validate total equals zero',
            'Post journal'
        ]
    },
    'finance_tax_calculation': {
        'keywords': ['tax', 'invoice', 'ledger'],
        'steps': [
            'Navigate to Finance > Taxes > Reports',
            'Generate Tax Summary for period',
            'Verify tax rate application',
            'Check against ledger totals'
        ]
    },
    'finance_voucher_creation': {
        'keywords': ['voucher', 'payment', 'journal'],
        'steps': [
            'Navigate to Finance > Payables > Vouchers',
            'Enter vendor and amount',
            'Select expense account',
            'Save and post voucher'
        ]
    },
    # HR
    'hr_employee_onboarding': {
        'keywords': ['employee', 'onboarding', 'recruitment'],
        'steps': [
            'Navigate to HR > Employees > New Hire',
            'Enter personal details',
            'Assign department and role',
            'Complete onboarding checklist'
        ]
    },
    'hr_leave_approval': {
        'keywords': ['leave', 'attendance', 'approval'],
        'steps': [
            'Navigate to HR > Leave Management',
            'Select pending leave request',
            'Review leave balance',
            'Click Approve',
            'Verify status changes to Approved'
        ]
    },
    'hr_appraisal_submission': {
        'keywords': ['appraisal', 'employee'],
        'steps': [
            'Navigate to HR > Performance > Appraisals',
            'Select employee record',
            'Fill evaluation form',
            'Submit to manager'
        ]
    },
    'hr_attendance_correction': {
        'keywords': ['attendance', 'employee', 'leave'],
        'steps': [
            'Navigate to HR > Time & Attendance',
            'Select employee and date',
            'Edit punch in/out times',
            'Save changes'
        ]
    },
    'hr_termination_process': {
        'keywords': ['termination', 'employee'],
        'steps': [
            'Navigate to HR > Employees > Separation',
            'Initiate termination workflow',
            'Complete exit interview form',
            'Deactivate employee record'
        ]
    },
    # Payroll
    'payroll_salary_processing': {
        'keywords': ['salary', 'payslip', 'deduction'],
        'steps': [
            'Navigate to Payroll > Processing',
            'Select pay period',
            'Run calculation engine',
            'Review variance report',
            'Generate payslips'
        ]
    },
    'payroll_overtime_calc': {
        'keywords': ['overtime', 'salary'],
        'steps': [
            'Navigate to Payroll > Time Entry',
            'Verify overtime hours',
            'Apply overtime rate multiplier',
            'Check total calculated'
        ]
    },
    'payroll_bonus_payout': {
        'keywords': ['bonus', 'salary'],
        'steps': [
            'Navigate to Payroll > Additional Earnings',
            'Select employee',
            'Enter bonus amount',
            'Verify tax calculation on bonus'
        ]
    },
    'payroll_tax_deduction': {
        'keywords': ['tax', 'deduction', 'salary'],
        'steps': [
            'Navigate to Payroll > Deductions > Tax',
            'Review tax bracket configuration',
            'Run trial payroll',
            'Verify deducted amount'
        ]
    },
    'payroll_pf_contribution': {
        'keywords': ['pf', 'deduction', 'esi'],
        'steps': [
            'Navigate to Payroll > Statutory',
            'Check PF contribution rates',
            'Verify employer and employee share',
            'Generate PF report'
        ]
    },
    # Procurement
    'procurement_po_creation': {
        'keywords': ['purchase order', 'vendor'],
        'steps': [
            'Navigate to Procurement > Purchase Orders',
            'Select vendor',
            'Add items and quantities',
            'Save PO'
        ]
    },
    'procurement_po_approval': {
        'keywords': ['po approval', 'purchase order'],
        'steps': [
            'Navigate to Procurement > Approvals',
            'Select pending PO',
            'Verify budget limits',
            'Approve PO'
        ]
    },
    'procurement_goods_receipt': {
        'keywords': ['goods receipt', 'purchase order'],
        'steps': [
            'Navigate to Procurement > Receiving',
            'Select open PO',
            'Enter received quantities',
            'Post goods receipt'
        ]
    },
    'procurement_rfq_submission': {
        'keywords': ['rfq', 'vendor'],
        'steps': [
            'Navigate to Procurement > Sourcing > RFQs',
            'Create RFQ',
            'Add target vendors',
            'Publish RFQ'
        ]
    },
    'procurement_three_way_match': {
        'keywords': ['three-way match', 'purchase order', 'goods receipt'],
        'steps': [
            'Navigate to Procurement > Invoicing',
            'Select PO and Receipt',
            'Enter vendor invoice details',
            'Verify matching tolerances',
            'Post invoice'
        ]
    },
    # Inventory
    'inventory_stock_transfer': {
        'keywords': ['stock', 'transfer', 'warehouse'],
        'steps': [
            'Navigate to Inventory > Operations > Transfers',
            'Select source and destination warehouse',
            'Add items to transfer',
            'Confirm transfer'
        ]
    },
    'inventory_reorder_level': {
        'keywords': ['reorder', 'stock', 'warehouse'],
        'steps': [
            'Navigate to Inventory > Planning',
            'Run reorder point calculation',
            'Review suggested orders',
            'Convert to Purchase Orders'
        ]
    },
    'inventory_lot_tracking': {
        'keywords': ['lot', 'serial', 'stock'],
        'steps': [
            'Navigate to Inventory > Traceability',
            'Enter lot number',
            'View lot genealogy',
            'Check stock balance by lot'
        ]
    },
    'inventory_valuation': {
        'keywords': ['valuation', 'stock'],
        'steps': [
            'Navigate to Inventory > Reports',
            'Generate Inventory Valuation report',
            'Verify unit costs',
            'Check total value'
        ]
    },
    'inventory_bin_management': {
        'keywords': ['bin', 'warehouse', 'stock'],
        'steps': [
            'Navigate to Inventory > Warehouse Setup',
            'Select Bin Locations',
            'Update bin capacity',
            'Perform cycle count on bin'
        ]
    },
    # Manufacturing
    'manufacturing_work_order': {
        'keywords': ['work order', 'production'],
        'steps': [
            'Navigate to Manufacturing > Work Orders',
            'Create new WO for assembly',
            'Release WO to shop floor',
            'Check material availability'
        ]
    },
    'manufacturing_bom_creation': {
        'keywords': ['bom', 'production'],
        'steps': [
            'Navigate to Manufacturing > Master Data > BOM',
            'Create new BOM',
            'Add components and quantities',
            'Approve BOM'
        ]
    },
    'manufacturing_routing': {
        'keywords': ['routing', 'production', 'work order'],
        'steps': [
            'Navigate to Manufacturing > Routings',
            'Define operations sequence',
            'Assign work centers',
            'Calculate standard time'
        ]
    },
    'manufacturing_scrap_reporting': {
        'keywords': ['scrap', 'quality', 'production'],
        'steps': [
            'Navigate to Manufacturing > Execution',
            'Select active work order',
            'Report scrap quantity',
            'Select reason code'
        ]
    },
    'manufacturing_mrp_run': {
        'keywords': ['mrp', 'production'],
        'steps': [
            'Navigate to Manufacturing > Planning > MRP',
            'Set planning horizon',
            'Execute MRP run',
            'Review planned orders'
        ]
    },
    # CRM
    'crm_lead_conversion': {
        'keywords': ['lead', 'opportunity', 'contact'],
        'steps': [
            'Navigate to CRM > Leads',
            'Select qualified lead',
            'Click Convert',
            'Verify new Opportunity and Contact created'
        ]
    },
    'crm_opportunity_pipeline': {
        'keywords': ['opportunity', 'pipeline'],
        'steps': [
            'Navigate to CRM > Pipeline Board',
            'Drag opportunity to next stage',
            'Update probability',
            'Save changes'
        ]
    },
    'crm_campaign_creation': {
        'keywords': ['campaign', 'lead'],
        'steps': [
            'Navigate to CRM > Marketing > Campaigns',
            'Create new email campaign',
            'Select target list',
            'Schedule launch'
        ]
    },
    'crm_quote_generation': {
        'keywords': ['quote', 'opportunity'],
        'steps': [
            'Navigate to CRM > Quotes',
            'Create quote from Opportunity',
            'Add products and pricing',
            'Generate PDF'
        ]
    },
    'crm_follow_up_task': {
        'keywords': ['follow-up', 'contact', 'lead'],
        'steps': [
            'Navigate to CRM > Activities',
            'Create new Task',
            'Set due date and reminder',
            'Assign to sales rep'
        ]
    },
    # Sales
    'sales_order_entry': {
        'keywords': ['sales order', 'delivery'],
        'steps': [
            'Navigate to Sales > Orders',
            'Select customer',
            'Add line items',
            'Confirm order'
        ]
    },
    'sales_quotation_approval': {
        'keywords': ['quotation', 'discount'],
        'steps': [
            'Navigate to Sales > Quotations',
            'Apply special discount',
            'Submit for managerial approval',
            'Verify approval status'
        ]
    },
    'sales_delivery_processing': {
        'keywords': ['delivery', 'sales order'],
        'steps': [
            'Navigate to Sales > Deliveries',
            'Select open order',
            'Pick and pack items',
            'Post goods issue'
        ]
    },
    'sales_invoicing': {
        'keywords': ['invoice', 'sales order', 'delivery'],
        'steps': [
            'Navigate to Sales > Billing',
            'Select delivered order',
            'Generate invoice',
            'Post to accounting'
        ]
    },
    'sales_credit_note': {
        'keywords': ['credit note', 'invoice', 'discount'],
        'steps': [
            'Navigate to Sales > Returns',
            'Create return order',
            'Receive returned goods',
            'Generate credit note'
        ]
    },
    # Compliance
    'compliance_audit_log': {
        'keywords': ['audit', 'report', 'control'],
        'steps': [
            'Navigate to Settings > Security > Audit Logs',
            'Select date range and user',
            'Export activity report',
            'Verify sensitive data access'
        ]
    },
    'compliance_gdpr_deletion': {
        'keywords': ['gdpr', 'policy', 'regulation'],
        'steps': [
            'Navigate to Compliance > Data Privacy',
            'Search data subject',
            'Execute Right to be Forgotten process',
            'Verify data anonymization'
        ]
    },
    'compliance_sox_control': {
        'keywords': ['sox', 'control', 'audit'],
        'steps': [
            'Navigate to Compliance > SOX Dashboard',
            'Review segregation of duties conflicts',
            'Document compensating control',
            'Sign-off review'
        ]
    },
    'compliance_risk_assessment': {
        'keywords': ['risk', 'report', 'regulation'],
        'steps': [
            'Navigate to Compliance > Risk Management',
            'Create new assessment',
            'Score likelihood and impact',
            'Generate risk matrix'
        ]
    },
    'compliance_policy_update': {
        'keywords': ['policy', 'regulation'],
        'steps': [
            'Navigate to Compliance > Document Control',
            'Draft new policy revision',
            'Route for electronic signatures',
            'Publish active version'
        ]
    }
}

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0

def predict_steps(description):
    desc_words = set(str(description).lower().split())
    
    best_template = None
    best_score = -1
    
    for tmpl_id, tmpl_data in TEMPLATES.items():
        kw_set = set(tmpl_data['keywords'])
        score = jaccard_similarity(desc_words, kw_set)
        if score > best_score:
            best_score = score
            best_template = tmpl_id
            
    if best_template:
        return TEMPLATES[best_template]['steps']
    return []

def evaluate_baseline(data_dir, output_dir):
    bugs_path = os.path.join(data_dir, 'bugs_cleaned.csv')
    resolutions_path = os.path.join(data_dir, 'resolutions_cleaned.csv')
    
    if not os.path.exists(bugs_path) or not os.path.exists(resolutions_path):
        print("Data files not found. Ensure the cleaning pipeline has been run.")
        return
        
    bugs_df = pd.read_csv(bugs_path)
    res_df = pd.read_csv(resolutions_path)

    # Merge and resolve duplicate column names from pandas suffix
    df = bugs_df.merge(res_df, on='bug_id', how='inner', suffixes=('', '_res'))

    test_size = int(len(df) * 0.15)
    test_df = df.tail(test_size).copy()
    
    if test_df.empty:
        print("Test set is empty.")
        return

    # Resolve the ground-truth reproducible_steps column
    steps_col = 'reproducible_steps'
    for candidate in ['reproducible_steps', 'reproducible_steps_res']:
        if candidate in test_df.columns:
            steps_col = candidate
            break

    predictions = []
    f1_scores = []
    precisions = []
    recalls = []
    
    for idx, row in test_df.iterrows():
        desc = row.get('description_clean', row.get('description', ''))
        pred_steps = predict_steps(desc)
        predictions.append(json.dumps(pred_steps))
        
        gt_steps_raw = row.get(steps_col, '[]')
        try:
            if isinstance(gt_steps_raw, str):
                gt_steps = json.loads(gt_steps_raw) if gt_steps_raw.startswith('[') else [gt_steps_raw]
            else:
                gt_steps = []
        except Exception:
            gt_steps = []

        # Token-level overlap: break each step into individual words
        def to_tokens(steps_list):
            return set(
                token
                for step in steps_list
                for token in str(step).lower().split()
                if len(token) > 2
            )

        pred_tokens = to_tokens(pred_steps)
        gt_tokens   = to_tokens(gt_steps)

        if not pred_tokens and not gt_tokens:
            precision = recall = f1 = 1.0
        elif not pred_tokens or not gt_tokens:
            precision = recall = f1 = 0.0
        else:
            intersection = len(pred_tokens & gt_tokens)
            precision = intersection / len(pred_tokens)
            recall    = intersection / len(gt_tokens)
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        
    test_df = test_df.copy()
    test_df['predicted_steps'] = predictions
    test_df['precision']       = precisions
    test_df['recall']          = recalls
    test_df['f1_score']        = f1_scores
    test_df['rsr_success']     = test_df['f1_score'] > 0.5
    
    avg_precision = sum(precisions) / len(precisions)
    avg_recall    = sum(recalls)    / len(recalls)
    avg_f1        = sum(f1_scores)  / len(f1_scores)
    rsr           = test_df['rsr_success'].mean()

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'baseline_results.csv')
    test_df.to_csv(out_path, index=False)
    
    print("=" * 50)
    print("    BASELINE EVALUATION REPORT")
    print("=" * 50)
    print(f"  Test Set Size:                 {len(test_df):,}")
    print(f"  Average Precision:             {avg_precision:.4f}  ({avg_precision:.2%})")
    print(f"  Average Recall:                {avg_recall:.4f}  ({avg_recall:.2%})")
    print(f"  Average F1-Score:              {avg_f1:.4f}  ({avg_f1:.2%})")
    print(f"  Reproduction Success Rate:     {rsr:.4f}  ({rsr:.2%})")
    print("=" * 50)
    print(f"  Results saved to: {out_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Baseline System")
    parser.add_argument('--data-dir', default='data/cleaned', help="Cleaned data directory")
    parser.add_argument('--output-dir', default='data', help="Output directory for results")
    args = parser.parse_args()
    
    evaluate_baseline(args.data_dir, args.output_dir)
