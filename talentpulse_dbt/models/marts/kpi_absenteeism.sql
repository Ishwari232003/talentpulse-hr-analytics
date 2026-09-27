-- Absenteeism KPI
-- Business question: How is absenteeism changing, what drives it, and what action should the business take?

SELECT
    e.department,
    DATE_TRUNC('month', a.date) AS month,
    COUNT(*) FILTER (WHERE a.status = 'Absent') AS absent_days,
    COUNT(*) AS total_recorded_days,
    ROUND(
        (COUNT(*) FILTER (WHERE a.status = 'Absent')::NUMERIC / COUNT(*)) * 100,
        2
    ) AS absenteeism_rate_pct
FROM {{ source('warehouse', 'fact_attendance') }} a
JOIN {{ source('warehouse', 'dim_employee') }} e
    ON a.employee_id = e.employee_id
GROUP BY e.department, DATE_TRUNC('month', a.date)
ORDER BY month DESC, absenteeism_rate_pct DESC