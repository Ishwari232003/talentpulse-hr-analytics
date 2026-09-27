

import psycopg2
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message):
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        print(f"Slack response: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Slack notification failed: {e}")

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="talentpulse",
    user="talentpulse",
    password="talentpulse"
)
cur = conn.cursor()

def create_alert(alert_type, severity, employee_id, department, reason, owner):
    cur.execute("""
        INSERT INTO alerts (alert_type, severity, employee_id, department, trigger_reason, owner)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (alert_type, severity, employee_id, department, reason, owner))

    if severity == "High":
        emp_text = f" | Employee: {employee_id}" if employee_id else ""
        dept_text = f" | Department: {department}" if department else ""
        message = f":rotating_light: *{alert_type}* ({severity}){emp_text}{dept_text}\nReason: {reason}\nOwner: {owner}"
        send_slack_alert(message)

alerts_created = 0

# ---------- RULE 1: High attrition risk -> manager workflow ----------
cur.execute("""
    WITH recent_absenteeism AS (
        SELECT employee_id,
               ROUND((COUNT(*) FILTER (WHERE status = 'Absent')::NUMERIC / COUNT(*)) * 100, 2) AS absent_pct
        FROM fact_attendance
        WHERE date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY employee_id
    ),
    latest_performance AS (
        SELECT DISTINCT ON (employee_id) employee_id, score
        FROM fact_performance
        ORDER BY employee_id, review_date DESC
    )
    SELECT ra.employee_id, e.department, ra.absent_pct, lp.score
    FROM recent_absenteeism ra
    JOIN latest_performance lp ON ra.employee_id = lp.employee_id
    JOIN dim_employee e ON ra.employee_id = e.employee_id
    WHERE ra.absent_pct > 15 AND lp.score < 3.0
""")
for emp_id, dept, absent_pct, score in cur.fetchall():
    reason = f"Absenteeism {absent_pct}% in last 30 days, performance score {score}"
    create_alert("High Attrition Risk", "High", emp_id, dept, reason, "Manager")
    alerts_created += 1

# ---------- RULE 2: Recruitment SLA breach -> recruiter alert ----------
cur.execute("""
    SELECT candidate_id, requisition_id, stage, stage_time, source
    FROM fact_recruitment
    WHERE stage_time > 30 AND stage NOT IN ('Hired', 'Rejected')
""")
for cand_id, req_id, stage, stage_time, source in cur.fetchall():
    reason = f"Candidate {cand_id} (req {req_id}) stuck at '{stage}' for {stage_time} days"
    create_alert("Recruitment SLA Breach", "Medium", None, None, reason, "Recruiter")
    alerts_created += 1

# ---------- RULE 3: Skill gap -> learning recommendation ----------
cur.execute("""
    SELECT employee_id, COUNT(*) AS gap_count
    FROM fact_learning
    WHERE completion_status IN ('Not Started', 'Failed')
    GROUP BY employee_id
    HAVING COUNT(*) >= 2
""")
for emp_id, gap_count in cur.fetchall():
    cur.execute("SELECT department FROM dim_employee WHERE employee_id = %s", (emp_id,))
    dept = cur.fetchone()[0]
    reason = f"{gap_count} incomplete/failed courses"
    create_alert("Skill Gap", "Medium", emp_id, dept, reason, "Learning Team")
    alerts_created += 1

# ---------- RULE 4: Absenteeism anomaly -> HR review ----------
cur.execute("""
    SELECT e.department,
           ROUND((COUNT(*) FILTER (WHERE a.status = 'Absent')::NUMERIC / COUNT(*)) * 100, 2) AS absent_pct
    FROM fact_attendance a
    JOIN dim_employee e ON a.employee_id = e.employee_id
    WHERE a.date >= DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY e.department
    HAVING (COUNT(*) FILTER (WHERE a.status = 'Absent')::NUMERIC / COUNT(*)) * 100 > 10
""")
for dept, absent_pct in cur.fetchall():
    reason = f"Department absenteeism at {absent_pct}% this month (threshold: 10%)"
    create_alert("Absenteeism Anomaly", "High", None, dept, reason, "HR")
    alerts_created += 1

conn.commit()
print(f"Automation run complete. {alerts_created} new alert(s) created.")

cur.close()
conn.close()