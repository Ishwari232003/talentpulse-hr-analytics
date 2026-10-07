import pandas as pd
import numpy as np
import os
import psycopg2
from psycopg2.extras import execute_values

import os

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5433"),
    dbname="talentpulse",
    user="talentpulse",
    password="talentpulse"
)
cur = conn.cursor()

def clean(df):
    """Convert pandas NaN into Python None so psycopg2 handles it correctly."""
    return df.replace({np.nan: None})

# ---------- Clear old data first (safe to re-run) ----------
cur.execute("TRUNCATE fact_recruitment, fact_attendance, fact_learning, fact_performance, fact_exits RESTART IDENTITY;")
cur.execute("TRUNCATE dim_employee CASCADE;")
conn.commit()

# ---------- 1. Employees ----------
employees = clean(pd.read_csv("../data_generator/employees.csv"))
rows = list(employees.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO dim_employee (employee_id, department, role, location, join_date, manager_id)
    VALUES %s
    ON CONFLICT (employee_id) DO NOTHING
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into dim_employee")

# ---------- 2. Recruitment ----------
recruitment = clean(pd.read_csv("../data_generator/recruitment.csv"))
rows = list(recruitment.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO fact_recruitment (candidate_id, requisition_id, stage, stage_time, source, cost)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_recruitment")



# ---------- 3. Attendance ----------
attendance = clean(pd.read_csv("../data_generator/attendance.csv"))
rows = list(attendance.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO fact_attendance (employee_id, date, status, hours)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_attendance")

# ---------- 4. Learning ----------
learning = pd.read_csv("../data_generator/learning.csv")
# Force score to proper nullable integer type, avoids "out of range" issues
learning["score"] = pd.to_numeric(learning["score"], errors="coerce")
learning = clean(learning)
rows = []
for r in learning.itertuples(index=False, name=None):
    emp_id, course_id, status, score = r
    score = None if score is None or (isinstance(score, float) and np.isnan(score)) else int(score)
    rows.append((emp_id, course_id, status, score))
execute_values(cur, """
    INSERT INTO fact_learning (employee_id, course_id, completion_status, score)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_learning")

# ---------- 5. Performance ----------
performance = clean(pd.read_csv("../data_generator/performance.csv"))
rows = list(performance.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO fact_performance (employee_id, review_date, score, goal_completion)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_performance")

# ---------- 6. Exits ----------
exits = clean(pd.read_csv("../data_generator/exits.csv"))
rows = list(exits.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO fact_exits (employee_id, exit_date, reason)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_exits")


# ---------- 7. Role Changes ----------
role_changes = clean(pd.read_csv("../data_generator/role_changes.csv"))
rows = list(role_changes.itertuples(index=False, name=None))
execute_values(cur, """
    INSERT INTO fact_role_change (employee_id, old_department, new_department, old_role, new_role, change_date)
    VALUES %s
""", rows)
conn.commit()
print(f"Loaded {len(rows)} rows into fact_role_change")




cur.close()
conn.close()
print("All data loaded successfully!")