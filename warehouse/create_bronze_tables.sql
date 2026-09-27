CREATE TABLE IF NOT EXISTS bronze.employees (
    employee_id TEXT, department TEXT, role TEXT, location TEXT,
    join_date TEXT, manager_id TEXT, ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.recruitment (
    candidate_id TEXT, requisition_id TEXT, stage TEXT, stage_time TEXT,
    source TEXT, cost TEXT, ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.attendance (
    employee_id TEXT, date TEXT, status TEXT, hours TEXT,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.learning (
    employee_id TEXT, course_id TEXT, completion_status TEXT, score TEXT,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.performance (
    employee_id TEXT, review_date TEXT, score TEXT, goal_completion TEXT,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.exits (
    employee_id TEXT, exit_date TEXT, reason TEXT,
    ingested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS bronze.role_changes (
    employee_id TEXT, old_department TEXT, new_department TEXT,
    old_role TEXT, new_role TEXT, change_date TEXT,
    ingested_at TIMESTAMP DEFAULT NOW()
);