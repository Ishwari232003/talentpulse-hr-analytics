-- Time-to-Hire KPI
-- Business question: How is time-to-hire changing, what drives it, and what action should the business take?

SELECT
    source,
    COUNT(*) FILTER (WHERE stage = 'Hired') AS total_hires,
    ROUND(AVG(stage_time) FILTER (WHERE stage = 'Hired'), 1) AS avg_days_to_hire,
    MIN(stage_time) FILTER (WHERE stage = 'Hired') AS fastest_hire_days,
    MAX(stage_time) FILTER (WHERE stage = 'Hired') AS slowest_hire_days
FROM {{ source('warehouse', 'fact_recruitment') }}
GROUP BY source
ORDER BY avg_days_to_hire DESC