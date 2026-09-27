# TalentPulse — Data Dictionary

All tables live in the `talentpulse` PostgreSQL database. Core warehouse tables are in the `public` schema; raw ingested data lives in the `bronze` schema; analytics KPI views are created by dbt (also in `public`, prefixed `kpi_`).

---

## Dimension Tables

### `dim_employee`
Master record for every employee.

| Column | Type | Description |
|---|---|---|
| employee_id | VARCHAR(10), PK | Unique employee identifier, e.g. `EMP0001` |
| department | VARCHAR(50) | Department name (Engineering, Sales, HR, Finance, Marketing, Operations, Support) |
| role | VARCHAR(50) | Job title/level (Associate, Senior Associate, Team Lead, Manager, Senior Manager, Director) |
| location | VARCHAR(50) | Office location or Remote |
| join_date | DATE | Date the employee joined the company |
| manager_id | VARCHAR(10) | employee_id of the employee's manager (nullable for top-level staff) |

### `dim_date`
Standard date dimension (currently populated as needed by queries; not pre-populated as a full calendar table).

| Column | Type | Description |
|---|---|---|
| date | DATE, PK | Calendar date |
| day | INT | Day of month |
| month | INT | Month number |
| quarter | INT | Quarter (1-4) |
| year | INT | Year |
| is_weekend | BOOLEAN | Whether the date falls on a weekend |

---

## Fact Tables

### `fact_recruitment`
One row per candidate application.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| candidate_id | VARCHAR(10) | Candidate identifier, e.g. `CAND0001` |
| requisition_id | VARCHAR(10) | Job requisition the candidate applied to |
| stage | VARCHAR(20) | Current pipeline stage: Applied, Screening, Interview, Offer, Hired, Rejected |
| stage_time | INT | Days spent in the current/final stage |
| source | VARCHAR(50) | Recruitment channel: LinkedIn, Referral, Naukri, Campus, Agency, Company Website |
| cost | NUMERIC(10,2) | Estimated cost (₹) attributed to this candidate's recruitment, varies by source |
| loaded_at | TIMESTAMP | Audit column — when this row was loaded |

### `fact_attendance`
One row per employee per working day (or per streamed live event).

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| employee_id | VARCHAR(10), FK → dim_employee | Employee this record belongs to |
| date | DATE | Attendance date |
| status | VARCHAR(20) | Present, Absent, Half-Day, Leave, WFH |
| hours | INT | Hours worked that day (8 = Present, 4 = Half-Day, 0 = Absent/Leave/WFH default in generator) |
| loaded_at | TIMESTAMP | Audit column |

### `fact_learning`
One row per course assigned to an employee.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| employee_id | VARCHAR(10), FK → dim_employee | Employee assigned the course |
| course_id | VARCHAR(20) | Course identifier, e.g. `COURSE001` |
| completion_status | VARCHAR(20) | Completed, In Progress, Not Started, Failed |
| score | INT | Score achieved (only populated when Completed; NULL otherwise) |
| loaded_at | TIMESTAMP | Audit column |

### `fact_performance`
One row per employee per quarterly review cycle.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| employee_id | VARCHAR(10), FK → dim_employee | Employee being reviewed |
| review_date | DATE | End date of the review period |
| score | NUMERIC(3,1) | Performance score, 1.0–5.0 |
| goal_completion | NUMERIC(3,2) | Fraction of goals completed, 0.0–1.0 |
| loaded_at | TIMESTAMP | Audit column |

### `fact_exits`
One row per employee who has left the company.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| employee_id | VARCHAR(10), FK → dim_employee | Employee who exited |
| exit_date | DATE | Date of exit |
| reason | VARCHAR(50) | Better Opportunity, Relocation, Personal Reasons, Performance, Higher Studies, Retirement |
| loaded_at | TIMESTAMP | Audit column |

### `fact_role_change`
One row per internal promotion or department transfer (supports the Internal Mobility KPI).

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Internal row ID |
| employee_id | VARCHAR(10), FK → dim_employee | Employee who moved |
| old_department | VARCHAR(50) | Department before the move |
| new_department | VARCHAR(50) | Department after the move (same as old_department if it was a promotion, not a transfer) |
| old_role | VARCHAR(50) | Role before the move |
| new_role | VARCHAR(50) | Role after the move |
| change_date | DATE | Date the change took effect |
| loaded_at | TIMESTAMP | Audit column |

---

## Operational Tables

### `alerts`
Output of the automation/decisioning engine — one row per triggered business rule.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Alert ID |
| alert_type | VARCHAR(50) | High Attrition Risk, Recruitment SLA Breach, Skill Gap, Absenteeism Anomaly |
| severity | VARCHAR(20) | High or Medium |
| employee_id | VARCHAR(10) | Related employee (nullable — some alerts, like recruitment/department ones, aren't employee-specific) |
| department | VARCHAR(50) | Related department (nullable) |
| trigger_reason | TEXT | Human-readable explanation of why the alert fired |
| status | VARCHAR(20) | Open (default) or Acknowledged |
| owner | VARCHAR(50) | Who should act: Manager, Recruiter, Learning Team, HR |
| created_at | TIMESTAMP | When the alert was generated |
| acknowledged_at | TIMESTAMP | When the alert was acknowledged (NULL if still open) |
| acknowledged_by | VARCHAR(50) | Who acknowledged it (currently unused/NULL — reserved for future auth integration) |

### `data_quality_log`
Output of the data quality check suite — one row per check, per run.

| Column | Type | Description |
|---|---|---|
| id | SERIAL, PK | Log entry ID |
| check_name | VARCHAR(100) | Name of the specific check, e.g. "Null employee_id in dim_employee" |
| check_category | VARCHAR(50) | Null Check, Duplicate Check, Uniqueness Check, Referential Integrity, Business Rule Check, Freshness Check, Volume Check |
| status | VARCHAR(20) | PASS or FAIL |
| details | TEXT | Specific result, e.g. "0 null employee_id(s) found" |
| checked_at | TIMESTAMP | When the check was run |

---

## Bronze Schema (raw, immutable ingestion layer)

Mirrors the source CSVs exactly — all columns stored as TEXT, no type conversion or validation, with only an `ingested_at` timestamp added. Tables: `bronze.employees`, `bronze.recruitment`, `bronze.attendance`, `bronze.learning`, `bronze.performance`, `bronze.exits`, `bronze.role_changes`. Column names match the corresponding warehouse table above (see each table's field list); the `cost` field, for example, is `bronze.recruitment.cost` (TEXT) vs. `fact_recruitment.cost` (NUMERIC).

---

## KPI Views (dbt-managed, Gold layer)

All are Postgres VIEWs, rebuilt by `dbt run`. Full SQL definitions live in `talentpulse_dbt/models/marts/`.

| View | Grain | Key output columns |
|---|---|---|
| `kpi_attrition_rate` | Exit month × reason | exit_count, total_employees, attrition_rate_pct |
| `kpi_cost_per_hire` | Recruitment source | total_hires, avg_cost_per_hire, total_hiring_cost |
| `kpi_time_to_hire` | Recruitment source | total_hires, avg_days_to_hire, fastest/slowest_hire_days |
| `kpi_absenteeism` | Department × month | absent_days, total_recorded_days, absenteeism_rate_pct |
| `kpi_training_completion` | Department | total_enrollments, completed_count, completion_rate_pct, avg_score |
| `kpi_performance_trend` | Department × review_date | avg_performance_score, avg_goal_completion_pct |
| `kpi_internal_mobility` | Month | promotions, transfers, total_moves, internal_mobility_rate_pct |
