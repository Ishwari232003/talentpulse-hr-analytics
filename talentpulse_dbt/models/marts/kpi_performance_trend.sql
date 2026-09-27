-- Performance Trend KPI
-- Business question: How is performance trend changing, what drives it, and what action should the business take?

SELECT
    e.department,
    p.review_date,
    ROUND(AVG(p.score), 2) AS avg_performance_score,
    ROUND(AVG(p.goal_completion) * 100, 2) AS avg_goal_completion_pct
FROM {{ source('warehouse', 'fact_performance') }} p
JOIN {{ source('warehouse', 'dim_employee') }} e
    ON p.employee_id = e.employee_id
GROUP BY e.department, p.review_date
ORDER BY p.review_date DESC, avg_performance_score DESC