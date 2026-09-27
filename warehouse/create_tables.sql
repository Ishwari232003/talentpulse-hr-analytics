-- ============ DIMENSION TABLES ============

CREATE TABLE IF NOT EXISTS dim_employee (
    employee_id VARCHAR(10) PRIMARY KEY,
    department VARCHAR(50),
    role VARCHAR(50),
    location VARCHAR(50),
    join_date DATE,
    manager_id VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date DATE PRIMARY KEY,
    day INT,
    month INT,
    quarter INT,
    year INT,
    is_weekend BOOLEAN
);

-- ============ FACT TABLES ============

CREATE TABLE IF NOT EXISTS fact_recruitment (
    id SERIAL PRIMARY KEY,
    candidate_id VARCHAR(10),
    requisition_id VARCHAR(10),
    stage VARCHAR(20),
    stage_time INT,
    source VARCHAR(50),
cost NUMERIC(10,2),
loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_attendance (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(10) REFERENCES dim_employee(employee_id),
    date DATE,
    status VARCHAR(20),
    hours INT,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_learning (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(10) REFERENCES dim_employee(employee_id),
    course_id VARCHAR(20),
    completion_status VARCHAR(20),
    score INT,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_performance (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(10) REFERENCES dim_employee(employee_id),
    review_date DATE,
    score NUMERIC(3,1),
    goal_completion NUMERIC(3,2),
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_exits (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(10) REFERENCES dim_employee(employee_id),
    exit_date DATE,
    reason VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fact_role_change (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(10) REFERENCES dim_employee(employee_id),
    old_department VARCHAR(50),
    new_department VARCHAR(50),
    old_role VARCHAR(50),
    new_role VARCHAR(50),
    change_date DATE,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_quality_log (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(200),
    check_category VARCHAR(100),
    status VARCHAR(20),
    details TEXT,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100),
    severity VARCHAR(20),
    employee_id VARCHAR(10),
    department VARCHAR(50),
    trigger_reason TEXT,
    owner VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);