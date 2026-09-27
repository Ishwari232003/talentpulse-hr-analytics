import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="talentpulse",
    user="talentpulse",
    password="talentpulse"
)
cur = conn.cursor()

def load_raw(csv_path, table_name, columns):
    df = pd.read_csv(csv_path, dtype=str)  # read everything as text (raw, unprocessed)
    df = df.where(pd.notnull(df), None)
    rows = list(df.itertuples(index=False, name=None))
    col_str = ", ".join(columns)
    execute_values(cur, f"""
        INSERT INTO bronze.{table_name} ({col_str})
        VALUES %s
    """, rows)
    conn.commit()
    print(f"Loaded {len(rows)} raw rows into bronze.{table_name}")

# Clear bronze tables first (safe to re-run)
cur.execute("""
    TRUNCATE bronze.employees, bronze.recruitment, bronze.attendance,
    bronze.learning, bronze.performance, bronze.exits, bronze.role_changes;
""")
conn.commit()

load_raw("../data_generator/employees.csv", "employees",
    ["employee_id", "department", "role", "location", "join_date", "manager_id"])

load_raw("../data_generator/recruitment.csv", "recruitment",
    ["candidate_id", "requisition_id", "stage", "stage_time", "source", "cost"])

load_raw("../data_generator/attendance.csv", "attendance",
    ["employee_id", "date", "status", "hours"])

load_raw("../data_generator/learning.csv", "learning",
    ["employee_id", "course_id", "completion_status", "score"])

load_raw("../data_generator/performance.csv", "performance",
    ["employee_id", "review_date", "score", "goal_completion"])

load_raw("../data_generator/exits.csv", "exits",
    ["employee_id", "exit_date", "reason"])

load_raw("../data_generator/role_changes.csv", "role_changes",
    ["employee_id", "old_department", "new_department", "old_role", "new_role", "change_date"])

cur.close()
conn.close()
print("All raw data loaded into Bronze layer successfully!")