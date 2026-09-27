import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
Faker.seed(42)

NUM_EMPLOYEES = 300
NUM_CANDIDATES = 500

departments = ["Engineering", "Sales", "HR", "Finance", "Marketing", "Operations", "Support"]
roles = ["Associate", "Senior Associate", "Team Lead", "Manager", "Senior Manager", "Director"]
locations = ["Bangalore", "Mumbai", "Delhi", "Pune", "Hyderabad", "Remote"]
recruitment_stages = ["Applied", "Screening", "Interview", "Offer", "Hired", "Rejected"]
recruitment_sources = ["LinkedIn", "Referral", "Naukri", "Campus", "Agency", "Company Website"]
attendance_status = ["Present", "Absent", "Half-Day", "Leave", "WFH"]
completion_status = ["Completed", "In Progress", "Not Started", "Failed"]
exit_reasons = ["Better Opportunity", "Relocation", "Personal Reasons", "Performance", "Higher Studies", "Retirement"]

# ---------------- 1. EMPLOYEES ----------------
employees = []
for i in range(1, NUM_EMPLOYEES + 1):
    join_date = fake.date_between(start_date="-5y", end_date="-30d")
    employees.append({
        "employee_id": f"EMP{i:04d}",
        "department": random.choice(departments),
        "role": random.choice(roles),
        "location": random.choice(locations),
        "join_date": join_date,
        "manager_id": f"EMP{random.randint(1, NUM_EMPLOYEES):04d}" if i > 20 else None
    })
employees_df = pd.DataFrame(employees)
employees_df.to_csv("employees.csv", index=False)

# ---------------- 2. RECRUITMENT ----------------
# Approximate average cost per hire, by source (₹) - reflects real-world patterns:
# agencies charge fees, referrals are cheap, job boards are mid-range
source_cost_ranges = {
    "LinkedIn": (8000, 15000),
    "Referral": (2000, 6000),
    "Naukri": (5000, 10000),
    "Campus": (3000, 7000),
    "Agency": (20000, 45000),
    "Company Website": (1000, 4000)
}

recruitment = []
for i in range(1, NUM_CANDIDATES + 1):
    stage = random.choice(recruitment_stages)
    stage_time = random.randint(1, 45)
    source = random.choice(recruitment_sources)
    cost_min, cost_max = source_cost_ranges[source]
    cost = random.randint(cost_min, cost_max)
    recruitment.append({
        "candidate_id": f"CAND{i:04d}",
        "requisition_id": f"REQ{random.randint(1, 80):03d}",
        "stage": stage,
        "stage_time": stage_time,
        "source": source,
        "cost": cost
    })
recruitment_df = pd.DataFrame(recruitment)
recruitment_df.to_csv("recruitment.csv", index=False)

# ---------------- 3. ATTENDANCE ----------------
attendance = []
start_date = datetime.today() - timedelta(days=90)
for emp in employees_df["employee_id"]:
    for day in range(90):
        date = start_date + timedelta(days=day)
        if date.weekday() >= 5:  # skip weekends
            continue
        status = random.choices(
            attendance_status, weights=[80, 5, 5, 5, 5]
        )[0]
        hours = 8 if status == "Present" else (4 if status == "Half-Day" else 0)
        attendance.append({
            "employee_id": emp,
            "date": date.date(),
            "status": status,
            "hours": hours
        })
attendance_df = pd.DataFrame(attendance)
attendance_df.to_csv("attendance.csv", index=False)

# ---------------- 4. LEARNING ----------------
learning = []
courses = [f"COURSE{i:03d}" for i in range(1, 31)]
for emp in employees_df["employee_id"]:
    num_courses = random.randint(1, 5)
    assigned_courses = random.sample(courses, num_courses)
    for course in assigned_courses:
        status = random.choice(completion_status)
        score = random.randint(40, 100) if status == "Completed" else None
        learning.append({
            "employee_id": emp,
            "course_id": course,
            "completion_status": status,
            "score": score
        })
learning_df = pd.DataFrame(learning)
learning_df.to_csv("learning.csv", index=False)

# ---------------- 5. PERFORMANCE ----------------
performance = []
review_dates = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]
for emp in employees_df["employee_id"]:
    for rd in review_dates:
        performance.append({
            "employee_id": emp,
            "review_date": rd,
            "score": round(random.uniform(1.0, 5.0), 1),
            "goal_completion": round(random.uniform(0.4, 1.0), 2)
        })
performance_df = pd.DataFrame(performance)
performance_df.to_csv("performance.csv", index=False)

# ---------------- 6. EXITS ----------------
num_exits = int(NUM_EMPLOYEES * 0.15)
exiting_employees = random.sample(list(employees_df["employee_id"]), num_exits)
exits = []
for emp in exiting_employees:
    exits.append({
        "employee_id": emp,
        "exit_date": fake.date_between(start_date="-1y", end_date="today"),
        "reason": random.choice(exit_reasons)
    })
exits_df = pd.DataFrame(exits)
exits_df.to_csv("exits.csv", index=False)

print("All 6 CSV files generated successfully:")
print("employees.csv, recruitment.csv, attendance.csv, learning.csv, performance.csv, exits.csv")


# ---------------- 7. ROLE CHANGES (Internal Mobility) ----------------
role_changes = []
num_movers = int(NUM_EMPLOYEES * 0.20)  # 20% of employees had at least one internal move
movers = random.sample(list(employees_df["employee_id"]), num_movers)

for emp in movers:
    emp_row = employees_df[employees_df["employee_id"] == emp].iloc[0]
    old_department = emp_row["department"]
    old_role = emp_row["role"]

    # 50% chance it's a promotion (same dept, higher role), 50% a department transfer
    if random.random() < 0.5:
        new_department = old_department
        new_role = random.choice(roles)
    else:
        new_department = random.choice([d for d in departments if d != old_department])
        new_role = random.choice(roles)

    change_date = fake.date_between(start_date="-2y", end_date="today")

    role_changes.append({
        "employee_id": emp,
        "old_department": old_department,
        "new_department": new_department,
        "old_role": old_role,
        "new_role": new_role,
        "change_date": change_date
    })

role_changes_df = pd.DataFrame(role_changes)
role_changes_df.to_csv("role_changes.csv", index=False)

print("All 7 CSV files generated successfully:")
print("employees.csv, recruitment.csv, attendance.csv, learning.csv, performance.csv, exits.csv, role_changes.csv")