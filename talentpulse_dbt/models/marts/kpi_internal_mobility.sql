-- Internal Mobility KPI
-- Business question: How is internal mobility changing, what drives it, and what action should the business take?

WITH total_headcount AS (
    SELECT COUNT(*) AS total_employees
    FROM {{ source('warehouse', 'dim_employee') }}
),

mobility_by_month AS (
    SELECT
        DATE_TRUNC('month', change_date) AS mobility_month,
        COUNT(*) FILTER (WHERE old_department = new_department) AS promotions,
        COUNT(*) FILTER (WHERE old_department != new_department) AS transfers,
        COUNT(*) AS total_moves
    FROM {{ source('warehouse', 'fact_role_change') }}
    GROUP BY DATE_TRUNC('month', change_date)
)

SELECT
    m.mobility_month,
    m.promotions,
    m.transfers,
    m.total_moves,
    t.total_employees,
    ROUND((m.total_moves::NUMERIC / t.total_employees) * 100, 2) AS internal_mobility_rate_pct
FROM mobility_by_month m
CROSS JOIN total_headcount t
ORDER BY m.mobility_month DESC