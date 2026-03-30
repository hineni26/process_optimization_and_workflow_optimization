# HR Process Optimization & Workflow Analytics

**Tech Stack:** Python · SQL (SQLite) · Power BI  
**Timeline:** Mar 2026 – Present

---

## Project Overview

Analyzed HR workflows across 300 employees to identify operational bottlenecks,
reduce onboarding inefficiencies, and support data-driven resource allocation decisions.

---

## Key Findings

| Metric | Value |
|---|---|
| Overall Attrition Rate | 23.3% |
| Highest Attrition Dept | Sales (31.4%) |
| Avg Onboarding Duration | 23.8 days |
| Onboarding Bottleneck | IT Setup (avg 9.7 days) |
| Leave Approval Rate | 88.4% |
| Avg Performance Score | 3.38 / 5.0 |
| High Performers | 14.0% of workforce |

---

## What Was Built

### 1. `generate_data.py`
Builds a realistic HR dataset with 4 tables:
- `employees` — 300 records with dept, level, salary, performance, attrition
- `onboarding` — 1,500 step-level records tracking each stage's duration
- `leave_requests` — 1,790 leave records with type, duration, approval
- `performance_reviews` — 492 semi-annual review records

### 2. `analyze.py`
Full Python analysis pipeline:
- Attrition analysis by department and job level
- Onboarding bottleneck detection (IT Setup = main delay)
- Leave & resource utilization by department
- Performance insights and high-performer segmentation
- Exports 5 Power BI-ready CSVs + dashboard PNG

### 3. `queries.sql`
8 structured SQL queries covering:
1. Attrition rate by department
2. Onboarding bottleneck per step
3. Employees with slowest onboarding (top 10)
4. Leave utilization & approval rate by department
5. Attrition risk scoring (performance + leave cross-analysis)
6. Performance trend by department
7. Salary vs performance (resource allocation efficiency)
8. Monthly attrition trend

### 4. Power BI Dashboard
Import these CSVs into Power BI for dashboards:
- `powerbi_kpi_summary.csv` — KPI cards
- `powerbi_attrition_by_dept.csv` — Bar chart
- `powerbi_onboarding_bottleneck.csv` — Funnel / bar
- `powerbi_leave_by_dept.csv` — Table / matrix
- `powerbi_performance_by_dept.csv` — Gauge / bar

---

## How to Run

```bash
# Step 1 — Install dependencies
pip install pandas numpy faker matplotlib

# Step 2 — Generate dataset
python generate_data.py

# Step 3 — Run analysis
python analyze.py

# Step 4 — Open SQL queries in DB Browser for SQLite
# File: output/hr_analytics.db

# Step 5 — Import CSVs from output/ into Power BI
```