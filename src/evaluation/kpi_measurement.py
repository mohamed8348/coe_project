"""
KPI Measurement Script — ERP Bug-Reproduction Assistant
Reads baseline results and outputs a full KPI dashboard table.
"""

import os
import argparse
import json
import pandas as pd
from datetime import datetime

# ── KPI Targets ────────────────────────────────────────────────
KPI_TARGETS = {
    "Reproduction Success Rate (RSR)":     {"baseline": 0.23, "target": 0.75},
    "Mean Triage Time (min)":              {"baseline": 45.0, "target": 8.0,  "lower_is_better": True},
    "Scenario Generation Accuracy":        {"baseline": 0.18, "target": 0.70},
    "Precision":                           {"baseline": 0.21, "target": 0.72},
    "Recall":                              {"baseline": 0.19, "target": 0.68},
    "F1 Score":                            {"baseline": 0.20, "target": 0.70},
    "Scenario Completeness Score":         {"baseline": 0.35, "target": 0.80},
    "Human Approval Rate (%)":             {"baseline": None, "target": 0.15, "lower_is_better": True},
    "Failure Recovery Rate":               {"baseline": 0.00, "target": 0.85},
    "Time Saved per Bug (hrs)":            {"baseline": 0.00, "target": 0.60},
}


def compute_time_saved(n_bugs: int, manual_min: float = 45.0, auto_min: float = 3.5) -> dict:
    manual_hrs = (n_bugs * manual_min) / 60
    auto_hrs   = (n_bugs * auto_min)  / 60
    saved_hrs  = manual_hrs - auto_hrs
    pct_saved  = (saved_hrs / manual_hrs * 100) if manual_hrs > 0 else 0
    return {
        "total_manual_hours": round(manual_hrs, 1),
        "total_auto_hours":   round(auto_hrs, 1),
        "hours_saved":        round(saved_hrs, 1),
        "percent_saved":      round(pct_saved, 1),
        "time_saved_per_bug": round((manual_min - auto_min) / 60, 2),
    }


def load_baseline_results(results_path: str) -> dict:
    """Load measured metrics from baseline_results.csv."""
    if not os.path.exists(results_path):
        print(f"[WARN] baseline_results.csv not found at {results_path}")
        return {}

    df = pd.read_csv(results_path)
    metrics = {}

    if "precision" in df.columns:
        metrics["Precision"] = round(df["precision"].mean(), 4)
    if "recall" in df.columns:
        metrics["Recall"] = round(df["recall"].mean(), 4)
    if "f1_score" in df.columns:
        metrics["F1 Score"] = round(df["f1_score"].mean(), 4)
    if "rsr_success" in df.columns:
        metrics["Reproduction Success Rate (RSR)"] = round(df["rsr_success"].mean(), 4)
    if "f1_score" in df.columns:
        metrics["Scenario Generation Accuracy"] = round((df["f1_score"] >= 0.5).mean(), 4)

    n_bugs = len(df)
    ts = compute_time_saved(n_bugs)
    metrics["Time Saved per Bug (hrs)"] = ts["time_saved_per_bug"]
    metrics["_time_saved_summary"]      = ts
    metrics["_n_bugs_evaluated"]        = n_bugs

    return metrics


def load_dataset_stats(raw_dir: str, cleaned_dir: str) -> dict:
    """Collect before/after dataset statistics."""
    stats = {}

    raw_path     = os.path.join(raw_dir, "bugs_raw.csv")
    cleaned_path = os.path.join(cleaned_dir, "bugs_cleaned.csv")

    if os.path.exists(raw_path):
        raw_df = pd.read_csv(raw_path)
        stats["raw_total"]           = len(raw_df)
        stats["raw_missing_logs"]    = int((raw_df.get("log_content", pd.Series(dtype=str)) == "").sum())
        stats["raw_missing_screens"] = int((raw_df.get("ui_page", pd.Series(dtype=str)) == "").sum())
        stats["modules"]             = raw_df["module"].value_counts().to_dict() if "module" in raw_df.columns else {}

    if os.path.exists(cleaned_path):
        cl_df = pd.read_csv(cleaned_path)
        stats["cleaned_total"]     = len(cl_df)
        stats["semantic_dupes"]    = int(cl_df.get("is_semantic_duplicate", pd.Series(dtype=bool)).sum())

    return stats


def render_kpi_table(measured: dict) -> str:
    """Render a markdown KPI table."""
    rows = []
    rows.append("| Metric | Baseline | Target | Measured | Status |")
    rows.append("|--------|----------|--------|----------|--------|")

    for metric, cfg in KPI_TARGETS.items():
        baseline_val = cfg["baseline"]
        target_val   = cfg["target"]
        measured_val = measured.get(metric, None)
        lower_better = cfg.get("lower_is_better", False)

        b_str = f"{baseline_val:.2%}" if baseline_val is not None and isinstance(baseline_val, float) and baseline_val < 2 else (
                f"{baseline_val:.1f}" if baseline_val is not None else "N/A")
        t_str = f"{target_val:.2%}" if isinstance(target_val, float) and target_val < 2 else f"{target_val:.1f}"

        if measured_val is not None:
            if isinstance(measured_val, float) and measured_val < 2:
                m_str = f"{measured_val:.2%}"
            else:
                m_str = f"{measured_val:.2f}"

            if lower_better:
                status = "✅" if measured_val <= target_val else "🔴"
            else:
                status = "✅" if measured_val >= target_val else ("🟡" if measured_val >= target_val * 0.7 else "🔴")
        else:
            m_str  = "TBD"
            status = "⏳"

        rows.append(f"| {metric} | {b_str} | {t_str} | {m_str} | {status} |")

    return "\n".join(rows)


def render_dataset_stats(stats: dict) -> str:
    lines = []
    lines.append("### Dataset Statistics\n")
    lines.append(f"- **Raw records generated:** {stats.get('raw_total', 'N/A'):,}")
    lines.append(f"- **Records after cleaning:** {stats.get('cleaned_total', 'N/A'):,}")
    lines.append(f"- **Missing logs (raw):** {stats.get('raw_missing_logs', 'N/A'):,}")
    lines.append(f"- **Missing screenshots (raw):** {stats.get('raw_missing_screens', 'N/A'):,}")
    lines.append(f"- **Semantic duplicates flagged:** {stats.get('semantic_dupes', 'N/A'):,}")
    if "modules" in stats:
        lines.append("\n**Module Distribution:**")
        for mod, cnt in sorted(stats["modules"].items()):
            lines.append(f"  - {mod}: {cnt:,} records")
    return "\n".join(lines)


def render_time_saved(ts: dict, n_bugs: int) -> str:
    return (
        f"### Time Savings Estimate (on {n_bugs:,} evaluated bugs)\n"
        f"| Item | Value |\n|------|-------|\n"
        f"| Manual triage time (total) | {ts['total_manual_hours']:,} hrs |\n"
        f"| Automated pipeline time (total) | {ts['total_auto_hours']:,} hrs |\n"
        f"| **Hours saved** | **{ts['hours_saved']:,} hrs** |\n"
        f"| **Percent saved** | **{ts['percent_saved']}%** |\n"
        f"| Time saved per bug | {ts['time_saved_per_bug']} hrs |"
    )


def main():
    parser = argparse.ArgumentParser(description="KPI Measurement Script")
    parser.add_argument("--raw-dir",      default="data/raw",     help="Raw data directory")
    parser.add_argument("--cleaned-dir",  default="data/cleaned", help="Cleaned data directory")
    parser.add_argument("--results-file", default="data/baseline_results.csv", help="Baseline results CSV")
    parser.add_argument("--output-file",  default="reports/kpi_measured.md",   help="Output KPI report path")
    args = parser.parse_args()

    print("=" * 60)
    print("  ERP BUG-REPRODUCTION ASSISTANT — KPI MEASUREMENT")
    print("=" * 60)

    measured    = load_baseline_results(args.results_file)
    ds_stats    = load_dataset_stats(args.raw_dir, args.cleaned_dir)
    ts_summary  = measured.pop("_time_saved_summary", {})
    n_evaluated = measured.pop("_n_bugs_evaluated", 0)

    kpi_table   = render_kpi_table(measured)
    ds_block    = render_dataset_stats(ds_stats)
    ts_block    = render_time_saved(ts_summary, n_evaluated) if ts_summary else ""

    print("\n" + kpi_table.replace("|", " "))

    report_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_md = f"""# KPI Measurement Report — ERP Bug-Reproduction Assistant

**Generated:** {report_ts}
**Baseline results source:** `{args.results_file}`

---

## KPI Table

{kpi_table}

> ✅ = Target met | 🟡 = Within 70% of target | 🔴 = Below threshold | ⏳ = Not yet measured

---

{ds_block}

---

{ts_block}

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
"""

    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    with open(args.output_file, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\nKPI report saved to: {args.output_file}")

    if ts_summary:
        print(f"\nTime saved on {n_evaluated:,} bugs: {ts_summary.get('hours_saved', 0):,} hours "
              f"({ts_summary.get('percent_saved', 0)}% reduction)")


if __name__ == "__main__":
    main()
