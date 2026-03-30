import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

conn = sqlite3.connect("output/hr_analytics.db")
df_emp     = pd.read_sql("SELECT * FROM employees",            conn)
df_onboard = pd.read_sql("SELECT * FROM onboarding",          conn)
df_leave   = pd.read_sql("SELECT * FROM leave_requests",      conn)
df_reviews = pd.read_sql("SELECT * FROM performance_reviews", conn)
conn.close()

print("=" * 60)
print("  HR PROCESS OPTIMIZATION & WORKFLOW ANALYTICS")
print("=" * 60)

print("\n[1] ATTRITION ANALYSIS")
print("-" * 40)

attrition_by_dept = df_emp.groupby("department")["is_active"].apply(
    lambda x: round((1 - x.mean()) * 100, 1)
).reset_index()
attrition_by_dept.columns = ["department", "attrition_rate_%"]
attrition_by_dept = attrition_by_dept.sort_values("attrition_rate_%", ascending=False)
print(attrition_by_dept.to_string(index=False))

attrition_by_level = df_emp.groupby("job_level")["is_active"].apply(
    lambda x: round((1 - x.mean()) * 100, 1)
).reset_index()
attrition_by_level.columns = ["job_level", "attrition_rate_%"]
print("\nAttrition by Job Level:")
print(attrition_by_level.to_string(index=False))

top_exit = df_emp[df_emp["is_active"] == 0]["exit_reason"].value_counts().head(5)
print("\nTop Exit Reasons:")
print(top_exit.to_string())


print("\n\n[2] ONBOARDING BOTTLENECK ANALYSIS")
print("-" * 40)

bottleneck = df_onboard.groupby("step")["days_taken"].agg(
    avg_days="mean", median_days="median", max_days="max", total_cases="count"
).round(1).sort_values("avg_days", ascending=False)
print(bottleneck.to_string())

worst_step = bottleneck["avg_days"].idxmax()
print(f"\nBottleneck Identified: '{worst_step}' takes the longest on average.")
print(f"Avg days: {bottleneck.loc[worst_step, 'avg_days']} | Max: {bottleneck.loc[worst_step, 'max_days']} days")

dept_onboard = df_onboard.groupby("department")["days_taken"].mean().round(1).sort_values(ascending=False)
print("\nAvg Onboarding Days per Department:")
print(dept_onboard.to_string())


print("\n\n[3] LEAVE & RESOURCE ALLOCATION")
print("-" * 40)

leave_by_dept = df_leave.groupby("department").agg(
    total_leave_days=("days_taken", "sum"),
    avg_leave_per_request=("days_taken", "mean"),
    total_requests=("days_taken", "count"),
    unapproved=("approved", lambda x: (~x.astype(bool)).sum())
).round(1).sort_values("total_leave_days", ascending=False)
print(leave_by_dept.to_string())

leave_by_type = df_leave.groupby("leave_type")["days_taken"].agg(
    total_days="sum", avg_days="mean", count="count"
).round(1).sort_values("total_days", ascending=False)
print("\nLeave by Type:")
print(leave_by_type.to_string())


print("\n\n[4] PERFORMANCE INSIGHTS")
print("-" * 40)

perf_dept = df_reviews.groupby("department")["score"].agg(
    avg_score="mean", std_dev="std", reviews="count"
).round(2).sort_values("avg_score", ascending=False)
print("Performance Score by Department:")
print(perf_dept.to_string())

high_perf = df_emp[df_emp["performance"] >= 4.0]
print(f"\nHigh Performers (score >= 4.0): {len(high_perf)} employees ({round(len(high_perf)/len(df_emp)*100,1)}%)")

underperf = df_emp[df_emp["performance"] < 2.5]
print(f"Underperformers (score < 2.5): {len(underperf)} employees ({round(len(underperf)/len(df_emp)*100,1)}%)")


print("\n\n[5] KEY EFFICIENCY METRICS")
print("-" * 40)

total_onboard_days = df_onboard.groupby("employee_id")["days_taken"].sum().mean()
print(f"Avg Total Onboarding Duration:   {round(total_onboard_days, 1)} days")
print(f"Overall Attrition Rate:          {round((1 - df_emp['is_active'].mean())*100, 1)}%")
print(f"Leave Approval Rate:             {round(df_leave['approved'].mean()*100, 1)}%")
print(f"Avg Performance Score:           {round(df_reviews['score'].mean(), 2)}/5.0")
print(f"Depts with >20% Attrition:       {(attrition_by_dept['attrition_rate_%'] > 20).sum()}")


summary_kpis = pd.DataFrame([
    {"metric": "Total Employees",          "value": len(df_emp)},
    {"metric": "Active Employees",         "value": df_emp["is_active"].sum()},
    {"metric": "Overall Attrition Rate %", "value": round((1 - df_emp["is_active"].mean())*100, 1)},
    {"metric": "Avg Onboarding Days",      "value": round(total_onboard_days, 1)},
    {"metric": "Onboarding Bottleneck",    "value": worst_step},
    {"metric": "Leave Approval Rate %",    "value": round(df_leave["approved"].mean()*100, 1)},
    {"metric": "Avg Performance Score",    "value": round(df_reviews["score"].mean(), 2)},
    {"metric": "High Performers",          "value": len(high_perf)},
])
summary_kpis.to_csv("output/powerbi_kpi_summary.csv", index=False)
attrition_by_dept.to_csv("output/powerbi_attrition_by_dept.csv", index=False)
bottleneck.reset_index().to_csv("output/powerbi_onboarding_bottleneck.csv", index=False)
leave_by_dept.reset_index().to_csv("output/powerbi_leave_by_dept.csv", index=False)
perf_dept.reset_index().to_csv("output/powerbi_performance_by_dept.csv", index=False)
print("\nPower BI CSVs exported to output/")


fig = plt.figure(figsize=(18, 12), facecolor="#0f1117")
fig.suptitle("HR Process Optimization & Workflow Analytics",
             fontsize=20, fontweight="bold", color="white", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

COLORS = ["#4fc3f7","#81c784","#ffb74d","#e57373","#ba68c8","#4dd0e1"]
ACCENT = "#4fc3f7"
BG     = "#1a1d27"
TEXT   = "#e0e0e0"

def style_ax(ax, title):
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")
    ax.set_title(title, color=TEXT, fontsize=11, fontweight="bold", pad=10)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)

ax1 = fig.add_subplot(gs[0, 0])
bars = ax1.barh(attrition_by_dept["department"], attrition_by_dept["attrition_rate_%"],
                color=COLORS, edgecolor="none")
for bar, val in zip(bars, attrition_by_dept["attrition_rate_%"]):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f"{val}%", va="center", ha="left", color=TEXT, fontsize=9)
style_ax(ax1, "Attrition Rate by Department")
ax1.set_xlabel("Attrition %")
ax1.set_xlim(0, attrition_by_dept["attrition_rate_%"].max() + 8)

ax2 = fig.add_subplot(gs[0, 1])
b_sorted = bottleneck.sort_values("avg_days")
bar_colors = ["#e57373" if s == worst_step else ACCENT for s in b_sorted.index]
bars2 = ax2.barh(b_sorted.index, b_sorted["avg_days"], color=bar_colors, edgecolor="none")
for bar, val in zip(bars2, b_sorted["avg_days"]):
    ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             f"{val}d", va="center", ha="left", color=TEXT, fontsize=9)
style_ax(ax2, "Onboarding Step Duration (Avg Days)")
ax2.set_xlabel("Avg Days")
red_patch = mpatches.Patch(color="#e57373", label="Bottleneck")
ax2.legend(handles=[red_patch], facecolor=BG, labelcolor=TEXT, fontsize=8)

ax3 = fig.add_subplot(gs[0, 2])
wedges, texts, autotexts = ax3.pie(
    leave_by_type["total_days"],
    labels=leave_by_type.index,
    autopct="%1.0f%%",
    colors=COLORS,
    startangle=90,
    textprops={"color": TEXT, "fontsize": 8},
    wedgeprops={"edgecolor": "#0f1117", "linewidth": 1.5}
)
for at in autotexts:
    at.set_color("white")
    at.set_fontsize(8)
ax3.set_title("Leave Distribution by Type", color=TEXT, fontsize=11, fontweight="bold", pad=10)

ax4 = fig.add_subplot(gs[1, 0])
perf_sorted = perf_dept.sort_values("avg_score")
bars4 = ax4.barh(perf_sorted.index, perf_sorted["avg_score"],
                 color=[COLORS[i % len(COLORS)] for i in range(len(perf_sorted))],
                 edgecolor="none")
ax4.axvline(x=3.0, color="#ffb74d", linestyle="--", linewidth=1.2, label="Threshold (3.0)")
for bar, val in zip(bars4, perf_sorted["avg_score"]):
    ax4.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
             f"{val:.2f}", va="center", ha="left", color=TEXT, fontsize=9)
style_ax(ax4, "Avg Performance Score by Dept")
ax4.set_xlabel("Score (out of 5.0)")
ax4.set_xlim(0, 5.5)
ax4.legend(facecolor=BG, labelcolor=TEXT, fontsize=8)

ax5 = fig.add_subplot(gs[1, 1])
level_order = ["Junior", "Mid", "Senior", "Lead", "Manager"]
attrition_level = df_emp.groupby("job_level")["is_active"].apply(
    lambda x: (1 - x.mean()) * 100
).reindex(level_order)
bars5 = ax5.bar(attrition_level.index, attrition_level.values,
                color=COLORS, edgecolor="none", width=0.6)
for bar, val in zip(bars5, attrition_level.values):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.1f}%", ha="center", va="bottom", color=TEXT, fontsize=9)
style_ax(ax5, "Attrition Rate by Job Level")
ax5.set_ylabel("Attrition %")

ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor(BG)
ax6.axis("off")
ax6.set_title("Key Efficiency Metrics", color=TEXT, fontsize=11, fontweight="bold", pad=10)

kpis = [
    ("Total Employees",     f"{len(df_emp)}"),
    ("Active Employees",    f"{int(df_emp['is_active'].sum())}"),
    ("Overall Attrition",   f"{round((1-df_emp['is_active'].mean())*100,1)}%"),
    ("Avg Onboarding Time", f"{round(total_onboard_days,1)} days"),
    ("Main Bottleneck",     worst_step),
    ("Leave Approval Rate", f"{round(df_leave['approved'].mean()*100,1)}%"),
    ("Avg Performance",     f"{round(df_reviews['score'].mean(),2)} / 5.0"),
    ("High Performers",     f"{len(high_perf)} ({round(len(high_perf)/len(df_emp)*100,1)}%)"),
]

for i, (label, value) in enumerate(kpis):
    y = 0.92 - i * 0.115
    ax6.text(0.02, y, label, transform=ax6.transAxes,
             fontsize=9, color="#9e9e9e", fontweight="normal")
    ax6.text(0.98, y, value, transform=ax6.transAxes,
             fontsize=9.5, color=ACCENT, fontweight="bold", ha="right")
    if i < len(kpis) - 1:
        ax6.plot([0.02, 0.98], [y - 0.055, y - 0.055], transform=ax6.transAxes,
                 color="#333", linewidth=0.5, clip_on=False)

plt.savefig("output/hr_analytics_dashboard.png", dpi=150, bbox_inches="tight",
            facecolor="#0f1117")
plt.close()
print("Dashboard saved.")