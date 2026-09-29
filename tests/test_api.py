import requests

BASE_URL = "http://127.0.0.1:8000"


def test_root_endpoint():
    """API root should respond with a running message."""
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_workforce_endpoint():
    """Workforce endpoint should return a non-empty list of department/location breakdowns."""
    r = requests.get(f"{BASE_URL}/api/workforce")
    assert r.status_code == 200
    data = r.json()
    assert "workforce" in data
    assert len(data["workforce"]) > 0
    assert "department" in data["workforce"][0]
    assert "headcount" in data["workforce"][0]


def test_recruitment_endpoint():
    """Recruitment funnel endpoint should return stage counts."""
    r = requests.get(f"{BASE_URL}/api/recruitment")
    assert r.status_code == 200
    data = r.json()
    assert "recruitment_funnel" in data
    assert len(data["recruitment_funnel"]) > 0


def test_employee_endpoint_valid_id():
    """A known employee ID should return full employee details."""
    r = requests.get(f"{BASE_URL}/api/employee/EMP0001")
    assert r.status_code == 200
    data = r.json()
    assert data["employee"]["employee_id"] == "EMP0001"
    assert "recent_attendance" in data
    assert "performance_history" in data


def test_employee_endpoint_invalid_id():
    """A non-existent employee ID should return 404."""
    r = requests.get(f"{BASE_URL}/api/employee/EMP9999")
    assert r.status_code == 404


def test_skill_gaps_endpoint():
    """Skill gaps endpoint should return employees with 2+ incomplete courses."""
    r = requests.get(f"{BASE_URL}/api/skill-gaps")
    assert r.status_code == 200
    data = r.json()
    assert "skill_gaps" in data
    if len(data["skill_gaps"]) > 0:
        assert data["skill_gaps"][0]["gap_count"] >= 2


def test_dashboard_endpoint_structure():
    """Dashboard endpoint should return all 7 KPI sections plus total employee count."""
    r = requests.get(f"{BASE_URL}/api/dashboard")
    assert r.status_code == 200
    data = r.json()
    expected_keys = [
        "total_employees", "attrition_rate", "cost_per_hire", "time_to_hire",
        "absenteeism", "training_completion", "performance_trend", "internal_mobility"
    ]
    for key in expected_keys:
        assert key in data
    assert data["total_employees"] == 300


def test_alerts_endpoint():
    """Alerts endpoint should return a list of alerts with required fields."""
    r = requests.get(f"{BASE_URL}/api/alerts")
    assert r.status_code == 200
    data = r.json()
    assert "alerts" in data
    if len(data["alerts"]) > 0:
        alert = data["alerts"][0]
        for field in ["id", "alert_type", "severity", "status", "owner", "trigger_reason"]:
            assert field in alert


def test_acknowledge_alert_invalid_id():
    """Acknowledging a non-existent alert ID should return 404."""
    r = requests.post(f"{BASE_URL}/api/alerts/999999/acknowledge")
    assert r.status_code == 404