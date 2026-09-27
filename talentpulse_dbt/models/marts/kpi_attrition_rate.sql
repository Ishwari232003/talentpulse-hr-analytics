-- Attrition Rate KPI
-- Business question: How is attrition changing, what drives it, and what action should the business take?

WITH total_headcount AS (
    SELECT COUNT(*) AS total_employees
    FROM {{ source('warehouse', 'dim_employee') }}
),

exits_by_month AS (
    SELECT
        DATE_TRUNC('month', exit_date) AS exit_month,
        COUNT(*) AS exit_count,
        reason
    FROM {{ source('warehouse', 'fact_exits') }}
    GROUP BY DATE_TRUNC('month', exit_date), reason
)

SELECT
    e.exit_month,
    e.reason,
    e.exit_count,
    t.total_employees,
    ROUND((e.exit_count::NUMERIC / t.total_employees) * 100, 2) AS attrition_rate_pct
FROM exits_by_month e
CROSS JOIN total_headcount t
ORDER BY e.exit_month DESC
