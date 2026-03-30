import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import sqlite3
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

DEPARTMENTS   = ["Engineering", "Sales", "HR", "Finance", "Operations", "Marketing"]
JOB_LEVELS    = ["Junior", "Mid", "Senior", "Lead", "Manager"]
EXIT_REASONS  = ["Better Opportunity", "Relocation", "Compensation", "Work-Life Balance",
                 "Management Issues", "Career Growth", "Personal", None]
ONBOARD_STEPS = ["Document Submission", "IT Setup", "Training", "Manager Briefing", "System Access"]
LEAVE_TYPES   = ["Annual", "Sick", "Unpaid", "Maternity/Paternity", "Emergency"]

N_EMPLOYEES = 300
START_DATE  = datetime(2023, 1, 1)
END_DATE    = datetime(2026, 3, 1)


def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


employees = []
for i in range(1, N_EMPLOYEES + 1):
    dept  = random.choice(DEPARTMENTS)
    level = random.choices(JOB_LEVELS, weights=[25, 35, 20, 12, 8])[0]
    join  = random_date(START_DATE, END_DATE - timedelta(days=180))

    attrition_prob = 0.25 if dept == "Sales" else 0.18
    attrition_prob += 0.10 if level == "Junior" else 0.0
    left = random.random() < attrition_prob

    exit_date   = random_date(join + timedelta(days=90), END_DATE) if left else None
    exit_reason = random.choice(EXIT_REASONS[:-1]) if left else None

    salary_base = {"Junior": 35000, "Mid": 55000, "Senior": 75000,
                   "Lead": 90000, "Manager": 110000}[level]
    salary = salary_base + random.randint(-5000, 15000)

    performance = round(np.random.normal(
        loc={"Junior": 3.0, "Mid": 3.3, "Senior": 3.6, "Lead": 3.8, "Manager": 3.7}[level],
        scale=0.5), 1)
    performance = max(1.0, min(5.0, performance))

    employees.append({
        "employee_id" : f"EMP{i:04d}",
        "name"        : fake.name(),
        "department"  : dept,
        "job_level"   : level,
        "join_date"   : join.strftime("%Y-%m-%d"),
        "exit_date"   : exit_date.strftime("%Y-%m-%d") if exit_date else None,
        "exit_reason" : exit_reason,
        "salary"      : salary,
        "performance" : performance,
        "manager_id"  : f"EMP{random.randint(1, 50):04d}",
        "location"    : random.choice(["HQ", "Remote", "Branch A", "Branch B"]),
        "is_active"   : not left
    })

df_emp = pd.DataFrame(employees)


onboarding = []
for _, emp in df_emp.iterrows():
    join_dt   = datetime.strptime(emp["join_date"], "%Y-%m-%d")
    step_date = join_dt
    for step in ONBOARD_STEPS:
        if step == "IT Setup":
            days = random.randint(5, 15)
        elif step == "System Access":
            days = random.randint(3, 10)
        else:
            days = random.randint(1, 4)

        completed = step_date + timedelta(days=days)
        onboarding.append({
            "employee_id" : emp["employee_id"],
            "department"  : emp["department"],
            "step"        : step,
            "step_start"  : step_date.strftime("%Y-%m-%d"),
            "step_end"    : completed.strftime("%Y-%m-%d"),
            "days_taken"  : days,
            "status"      : "Completed"
        })
        step_date = completed

df_onboard = pd.DataFrame(onboarding)


leaves = []
for _, emp in df_emp.iterrows():
    join_dt = datetime.strptime(emp["join_date"], "%Y-%m-%d")
    end_dt  = datetime.strptime(emp["exit_date"], "%Y-%m-%d") if pd.notna(emp["exit_date"]) else END_DATE
    months_active = max(1, (end_dt - join_dt).days // 30)
    n_leaves = random.randint(1, min(12, months_active))

    for _ in range(n_leaves):
        leave_start = random_date(join_dt, end_dt - timedelta(days=2))
        duration    = random.randint(1, 7)
        leaves.append({
            "employee_id" : emp["employee_id"],
            "department"  : emp["department"],
            "leave_type"  : random.choice(LEAVE_TYPES),
            "leave_start" : leave_start.strftime("%Y-%m-%d"),
            "leave_end"   : (leave_start + timedelta(days=duration)).strftime("%Y-%m-%d"),
            "days_taken"  : duration,
            "approved"    : random.choices([True, False], weights=[88, 12])[0]
        })

df_leave = pd.DataFrame(leaves)


reviews = []
for _, emp in df_emp.iterrows():
    join_dt = datetime.strptime(emp["join_date"], "%Y-%m-%d")
    end_dt  = datetime.strptime(emp["exit_date"], "%Y-%m-%d") if pd.notna(emp["exit_date"]) else END_DATE
    review_date = join_dt + timedelta(days=180)
    while review_date < end_dt:
        score = round(np.random.normal(emp["performance"], 0.3), 1)
        score = max(1.0, min(5.0, score))
        reviews.append({
            "employee_id" : emp["employee_id"],
            "department"  : emp["department"],
            "review_date" : review_date.strftime("%Y-%m-%d"),
            "score"       : score,
            "reviewer_id" : emp["manager_id"],
            "promoted"    : score >= 4.5 and random.random() < 0.3
        })
        review_date += timedelta(days=365)

df_reviews = pd.DataFrame(reviews)


os.makedirs("output", exist_ok=True)
df_emp.to_csv("output/employees.csv",              index=False)
df_onboard.to_csv("output/onboarding.csv",         index=False)
df_leave.to_csv("output/leave_requests.csv",       index=False)
df_reviews.to_csv("output/performance_reviews.csv",index=False)

print(f"Employees:           {len(df_emp)} rows")
print(f"Onboarding steps:    {len(df_onboard)} rows")
print(f"Leave requests:      {len(df_leave)} rows")
print(f"Performance reviews: {len(df_reviews)} rows")

conn = sqlite3.connect("output/hr_analytics.db")
df_emp.to_sql("employees",               conn, if_exists="replace", index=False)
df_onboard.to_sql("onboarding",          conn, if_exists="replace", index=False)
df_leave.to_sql("leave_requests",        conn, if_exists="replace", index=False)
df_reviews.to_sql("performance_reviews", conn, if_exists="replace", index=False)
conn.close()
print("SQLite DB saved: output/hr_analytics.db")