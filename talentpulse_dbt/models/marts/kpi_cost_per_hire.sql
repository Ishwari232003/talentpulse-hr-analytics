-- Cost-per-Hire KPI
-- Business question: How is cost-per-hire changing, what drives it, and what action should the business take?

SELECT
    source,
    COUNT(*) FILTER (WHERE stage = 'Hired') AS total_hires,
    ROUND(AVG(cost) FILTER (WHERE stage = 'Hired'), 2) AS avg_cost_per_hire,
    ROUND(SUM(cost) FILTER (WHERE stage = 'Hired'), 2) AS total_hiring_cost
FROM {{ source('warehouse', 'fact_recruitment') }}
GROUP BY source
ORDER BY avg_cost_per_hire DESC