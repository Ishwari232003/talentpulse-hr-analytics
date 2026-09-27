-- Training Completion KPI
-- Business question: How is training completion changing, what drives it, and what action should the business take?

SELECT
    e.department,
    COUNT(*) AS total_enrollments,
    COUNT(*) FILTER (WHERE l.completion_status = 'Completed') AS completed_count,
    ROUND(
        (COUNT(*) FILTER (WHERE l.completion_status = 'Completed')::NUMERIC / COUNT(*)) * 100,
        2
    ) AS completion_rate_pct,
    ROUND(AVG(l.score) FILTER (WHERE l.completion_status = 'Completed'), 1) AS avg_score
FROM {{ source('warehouse', 'fact_learning') }} l
JOIN {{ source('warehouse', 'dim_employee') }} e
    ON l.employee_id = e.employee_id
GROUP BY e.department
ORDER BY completion_rate_pct DESC