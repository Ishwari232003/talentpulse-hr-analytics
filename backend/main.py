from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras

app = FastAPI(title="TalentPulse API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5433,
        dbname="talentpulse",
        user="talentpulse",
        password="talentpulse",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

@app.get("/")
def root():
    return {"message": "TalentPulse API is running"}

# ---------- 1. Workforce Overview ----------
@app.get("/api/workforce")
def get_workforce():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT department, location, COUNT(*) as headcount
        FROM dim_employee
        GROUP BY department, location
        ORDER BY department
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"workforce": data}

# ---------- 2. Recruitment Funnel ----------
@app.get("/api/recruitment")
def get_recruitment():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stage, COUNT(*) as count
        FROM fact_recruitment
        GROUP BY stage
        ORDER BY count DESC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"recruitment_funnel": data}

# ---------- 3. Single Employee Details ----------
@app.get("/api/employee/{employee_id}")
def get_employee(employee_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM dim_employee WHERE employee_id = %s", (employee_id,))
    employee = cur.fetchone()
    if not employee:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Employee not found")

    cur.execute("SELECT * FROM fact_attendance WHERE employee_id = %s ORDER BY date DESC LIMIT 30", (employee_id,))
    attendance = cur.fetchall()

    cur.execute("SELECT * FROM fact_performance WHERE employee_id = %s ORDER BY review_date DESC", (employee_id,))
    performance = cur.fetchall()

    cur.execute("SELECT * FROM fact_learning WHERE employee_id = %s", (employee_id,))
    learning = cur.fetchall()

    cur.close()
    conn.close()
    return {
        "employee": employee,
        "recent_attendance": attendance,
        "performance_history": performance,
        "learning": learning
    }

# ---------- 4. Skill Gaps ----------
@app.get("/api/skill-gaps")
def get_skill_gaps():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.employee_id, e.department, COUNT(*) as gap_count
        FROM fact_learning l
        JOIN dim_employee e ON l.employee_id = e.employee_id
        WHERE l.completion_status IN ('Not Started', 'Failed')
        GROUP BY e.employee_id, e.department
        HAVING COUNT(*) >= 2
        ORDER BY gap_count DESC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"skill_gaps": data}

# ---------- 5. Dashboard (combined KPIs) ----------
@app.get("/api/dashboard")
def get_dashboard():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) as total_employees FROM dim_employee")
    total_employees = cur.fetchone()["total_employees"]

    cur.execute("SELECT * FROM kpi_attrition_rate LIMIT 5")
    attrition = cur.fetchall()

    cur.execute("SELECT * FROM kpi_cost_per_hire")
    cost_per_hire = cur.fetchall()

    cur.execute("SELECT * FROM kpi_time_to_hire")
    time_to_hire = cur.fetchall()

    cur.execute("SELECT * FROM kpi_absenteeism ORDER BY month DESC LIMIT 5")
    absenteeism = cur.fetchall()

    cur.execute("SELECT * FROM kpi_training_completion")
    training = cur.fetchall()

    cur.execute("SELECT * FROM kpi_performance_trend LIMIT 5")
    performance = cur.fetchall()

    cur.execute("SELECT * FROM kpi_internal_mobility LIMIT 5")
    mobility = cur.fetchall()

    cur.close()
    conn.close()
    return {
        "total_employees": total_employees,
        "attrition_rate": attrition,
        "cost_per_hire": cost_per_hire,
        "time_to_hire": time_to_hire,
        "absenteeism": absenteeism,
        "training_completion": training,
        "performance_trend": performance,
        "internal_mobility": mobility
    }

# ---------- 6. Alerts ----------
@app.get("/api/alerts")
def get_alerts(status: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if status:
        cur.execute("SELECT * FROM alerts WHERE status = %s ORDER BY created_at DESC", (status,))
    else:
        cur.execute("SELECT * FROM alerts ORDER BY created_at DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return {"alerts": data}

# ---------- 7. Acknowledge Alert ----------
@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE alerts
        SET status = 'Acknowledged', acknowledged_at = NOW()
        WHERE id = %s
        RETURNING *
    """, (alert_id,))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"acknowledged_alert": updated}