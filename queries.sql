-- ============================================================
-- HR Process Optimization & Workflow Analytics
-- SQL Queries (SQLite compatible)
-- ============================================================

-- ─────────────────────────────────────────────
-- 1. OVERALL ATTRITION RATE BY DEPARTMENT
-- ─────────────────────────────────────────────
SELECT
    department,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS attrited,
    ROUND(
        100.0 * SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS attrition_rate_pct
FROM employees
GROUP BY department
ORDER BY attrition_rate_pct DESC;


-- ─────────────────────────────────────────────
-- 2. ONBOARDING BOTTLENECK — AVG TIME PER STEP
-- ─────────────────────────────────────────────
SELECT
    step,
    ROUND(AVG(days_taken), 1)  AS avg_days,
    ROUND(MIN(days_taken), 0)  AS min_days,
    ROUND(MAX(days_taken), 0)  AS max_days,
    COUNT(*)                   AS employee_count
FROM onboarding
GROUP BY step
ORDER BY avg_days DESC;


-- ─────────────────────────────────────────────
-- 3. EMPLOYEES WITH SLOWEST ONBOARDING (TOP 10)
-- ─────────────────────────────────────────────
SELECT
    o.employee_id,
    e.department,
    e.job_level,
    SUM(o.days_taken) AS total_onboarding_days
FROM onboarding o
JOIN employees e ON o.employee_id = e.employee_id
GROUP BY o.employee_id, e.department, e.job_level
ORDER BY total_onboarding_days DESC
LIMIT 10;


-- ─────────────────────────────────────────────
-- 4. LEAVE UTILIZATION BY DEPARTMENT
-- ─────────────────────────────────────────────
SELECT
    department,
    SUM(days_taken)                   AS total_leave_days,
    COUNT(*)                          AS total_requests,
    ROUND(AVG(days_taken), 1)         AS avg_leave_days,
    SUM(CASE WHEN approved = 0 THEN 1 ELSE 0 END) AS rejected_requests,
    ROUND(
        100.0 * SUM(CASE WHEN approved = 1 THEN 1 ELSE 0 END) / COUNT(*), 1
    ) AS approval_rate_pct
FROM leave_requests
GROUP BY department
ORDER BY total_leave_days DESC;


-- ─────────────────────────────────────────────
-- 5. HIGH ATTRITION RISK: LOW PERFORMERS + HIGH LEAVE
-- ─────────────────────────────────────────────
SELECT
    e.employee_id,
    e.name,
    e.department,
    e.job_level,
    e.performance,
    COALESCE(l.total_leave, 0) AS total_leave_days,
    CASE
        WHEN e.performance < 2.5 AND COALESCE(l.total_leave, 0) > 15 THEN 'HIGH RISK'
        WHEN e.performance < 3.0 OR  COALESCE(l.total_leave, 0) > 20 THEN 'MEDIUM RISK'
        ELSE 'LOW RISK'
    END AS attrition_risk
FROM employees e
LEFT JOIN (
    SELECT employee_id, SUM(days_taken) AS total_leave
    FROM leave_requests
    GROUP BY employee_id
) l ON e.employee_id = l.employee_id
WHERE e.is_active = 1
ORDER BY attrition_risk, e.performance ASC
LIMIT 20;


-- ─────────────────────────────────────────────
-- 6. PERFORMANCE TREND BY DEPARTMENT
-- ─────────────────────────────────────────────
SELECT
    department,
    ROUND(AVG(score), 2)                              AS avg_score,
    ROUND(MIN(score), 1)                              AS min_score,
    ROUND(MAX(score), 1)                              AS max_score,
    SUM(CASE WHEN promoted = 1 THEN 1 ELSE 0 END)    AS promotions,
    COUNT(*)                                          AS reviews_count
FROM performance_reviews
GROUP BY department
ORDER BY avg_score DESC;


-- ─────────────────────────────────────────────
-- 7. SALARY VS PERFORMANCE (RESOURCE ALLOCATION)
-- ─────────────────────────────────────────────
SELECT
    job_level,
    ROUND(AVG(salary), 0)       AS avg_salary,
    ROUND(AVG(performance), 2)  AS avg_performance,
    COUNT(*)                    AS headcount,
    ROUND(AVG(salary) / AVG(performance), 0) AS salary_per_performance_unit
FROM employees
WHERE is_active = 1
GROUP BY job_level
ORDER BY salary_per_performance_unit;


-- ─────────────────────────────────────────────
-- 8. MONTHLY ATTRITION TREND
-- ─────────────────────────────────────────────
SELECT
    STRFTIME('%Y-%m', exit_date)   AS exit_month,
    department,
    COUNT(*)                        AS exits
FROM employees
WHERE is_active = 0
  AND exit_date IS NOT NULL
GROUP BY exit_month, department
ORDER BY exit_month DESC, exits DESC
LIMIT 30;
