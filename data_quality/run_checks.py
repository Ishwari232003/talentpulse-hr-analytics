import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="talentpulse",
    user="talentpulse",
    password="talentpulse"
)
cur = conn.cursor()

results = []

def log_check(name, category, passed, details):
    status = "PASS" if passed else "FAIL"
    cur.execute("""
        INSERT INTO data_quality_log (check_name, check_category, status, details)
        VALUES (%s, %s, %s, %s)
    """, (name, category, status, details))
    results.append((name, status, details))
    print(f"[{status}] {name}: {details}")

# ---------- 1. NULL CHECKS ----------
cur.execute("SELECT COUNT(*) FROM dim_employee WHERE employee_id IS NULL")
null_emp_ids = cur.fetchone()[0]
log_check("Null employee_id in dim_employee", "Null Check", null_emp_ids == 0,
           f"{null_emp_ids} null employee_id(s) found")

cur.execute("SELECT COUNT(*) FROM fact_attendance WHERE status IS NULL")
null_status = cur.fetchone()[0]
log_check("Null status in fact_attendance", "Null Check", null_status == 0,
           f"{null_status} null status value(s) found")

# ---------- 2. DUPLICATE CHECKS ----------
cur.execute("""
    SELECT COUNT(*) FROM (
        SELECT employee_id, date, COUNT(*) c
        FROM fact_attendance
        GROUP BY employee_id, date
        HAVING COUNT(*) > 1
    ) dup
""")
dup_attendance = cur.fetchone()[0]
log_check("Duplicate attendance records (same employee+date)", "Duplicate Check", dup_attendance == 0,
           f"{dup_attendance} duplicate employee+date combination(s) found")

# ---------- 3. UNIQUENESS CHECKS ----------
cur.execute("SELECT COUNT(*) - COUNT(DISTINCT employee_id) FROM dim_employee")
dup_emp = cur.fetchone()[0]
log_check("Employee ID uniqueness in dim_employee", "Uniqueness Check", dup_emp == 0,
           f"{dup_emp} duplicate employee_id(s) found")

# ---------- 4. REFERENTIAL INTEGRITY ----------
cur.execute("""
    SELECT COUNT(*) FROM fact_attendance a
    LEFT JOIN dim_employee e ON a.employee_id = e.employee_id
    WHERE e.employee_id IS NULL
""")
orphan_attendance = cur.fetchone()[0]
log_check("Referential integrity: fact_attendance -> dim_employee", "Referential Integrity",
           orphan_attendance == 0, f"{orphan_attendance} attendance record(s) with no matching employee")

cur.execute("""
    SELECT COUNT(*) FROM fact_performance p
    LEFT JOIN dim_employee e ON p.employee_id = e.employee_id
    WHERE e.employee_id IS NULL
""")
orphan_perf = cur.fetchone()[0]
log_check("Referential integrity: fact_performance -> dim_employee", "Referential Integrity",
           orphan_perf == 0, f"{orphan_perf} performance record(s) with no matching employee")

# ---------- 5. VALID-RANGE / BUSINESS-RULE CHECKS ----------
cur.execute("SELECT COUNT(*) FROM fact_performance WHERE score < 1.0 OR score > 5.0")
invalid_scores = cur.fetchone()[0]
log_check("Performance score within valid range (1-5)", "Business Rule Check", invalid_scores == 0,
           f"{invalid_scores} out-of-range performance score(s) found")

cur.execute("SELECT COUNT(*) FROM fact_attendance WHERE hours < 0 OR hours > 12")
invalid_hours = cur.fetchone()[0]
log_check("Attendance hours within valid range (0-12)", "Business Rule Check", invalid_hours == 0,
           f"{invalid_hours} out-of-range hours value(s) found")

# ---------- 6. FRESHNESS & VOLUME CHECKS ----------
cur.execute("SELECT MAX(date) FROM fact_attendance")
latest_date = cur.fetchone()[0]
days_old = (datetime.now().date() - latest_date).days if latest_date else None
log_check("Attendance data freshness", "Freshness Check", days_old is not None and days_old <= 7,
           f"Latest attendance record is {days_old} day(s) old")

cur.execute("SELECT COUNT(*) FROM dim_employee")
emp_count = cur.fetchone()[0]
log_check("Employee volume check (expect > 0)", "Volume Check", emp_count > 0,
           f"{emp_count} employee record(s) found")

conn.commit()

# ---------- Summary ----------
passed = sum(1 for r in results if r[1] == "PASS")
failed = sum(1 for r in results if r[1] == "FAIL")
print(f"\nData Quality Run Complete: {passed} passed, {failed} failed out of {len(results)} checks.")

cur.close()
conn.close()