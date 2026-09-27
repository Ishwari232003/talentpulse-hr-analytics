import { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from "recharts";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const COLORS = ["#4f46e5", "#06b6d4", "#f59e0b", "#ef4444", "#10b981", "#8b5cf6", "#ec4899"];

function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [recruitment, setRecruitment] = useState([]);
  const [skillGaps, setSkillGaps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [dashRes, alertsRes, recruitRes, skillRes] = await Promise.all([
        axios.get(`${API_BASE}/api/dashboard`),
        axios.get(`${API_BASE}/api/alerts`),
        axios.get(`${API_BASE}/api/recruitment`),
        axios.get(`${API_BASE}/api/skill-gaps`),
      ]);
      setDashboard(dashRes.data);
      setAlerts(alertsRes.data.alerts);
      setRecruitment(recruitRes.data.recruitment_funnel);
      setSkillGaps(skillRes.data.skill_gaps);
      setError(null);
    } catch (err) {
      setError("Could not connect to API. Is the backend running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const acknowledgeAlert = async (id) => {
    try {
      await axios.post(`${API_BASE}/api/alerts/${id}/acknowledge`);
      fetchData();
    } catch (err) {
      console.error("Failed to acknowledge alert", err);
    }
  };

  if (loading) return <div className="center-message">Loading TalentPulse...</div>;
  if (error) return <div className="center-message error">{error}</div>;

  const openAlerts = alerts.filter(
  a => a.status === "New" || a.status === "Open"
);

  return (
    <div className="app">
      <header className="header">
        <h1>TalentPulse</h1>
        <span className="live-dot">● Live</span>
      </header>

      <nav className="tabs">
        {["dashboard", "recruitment", "skill-gaps", "alerts"].map(tab => (
          <button
            key={tab}
            className={activeTab === tab ? "tab active" : "tab"}
            onClick={() => setActiveTab(tab)}
          >
            {tab.replace("-", " ").toUpperCase()}
          </button>
        ))}
        <button className="refresh-btn" onClick={fetchData}>↻ Refresh</button>
      </nav>

      <main className="content">

        {activeTab === "dashboard" && dashboard && (
          <>
            <div className="kpi-cards">
              <div className="kpi-card">
                <h3>Total Employees</h3>
                <p className="kpi-value">{dashboard.total_employees}</p>
              </div>
              <div className="kpi-card">
                <h3>Open Alerts</h3>
                <p className="kpi-value">{openAlerts.length}</p>
              </div>
              <div className="kpi-card">
                <h3>Avg Cost/Hire (Top Source)</h3>
                <p className="kpi-value">₹{dashboard.cost_per_hire[0]?.avg_cost_per_hire}</p>
              </div>
              <div className="kpi-card">
                <h3>Avg Time-to-Hire</h3>
                <p className="kpi-value">{dashboard.time_to_hire[dashboard.time_to_hire.length-1]?.avg_days_to_hire} days</p>
              </div>
            </div>

            <div className="chart-grid">
              <div className="chart-box">
                <h3>Cost per Hire by Source</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={dashboard.cost_per_hire}>
                    <CartesianGrid strokeDasharray="3 3" />
                     <XAxis
                       dataKey="source"
                       interval={0}
                       angle={-25}
                       textAnchor="end"
                       height={60}
                       tick={{ fontSize: 11 }}
/>
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="avg_cost_per_hire" fill="#4f46e5" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Absenteeism by Department</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={dashboard.absenteeism}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="absenteeism_rate_pct" fill="#ef4444" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Training Completion by Department</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={dashboard.training_completion}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="completion_rate_pct" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="chart-box">
                <h3>Performance Trend (Latest Cycle)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={dashboard.performance_trend}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="department" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="avg_performance_score" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </>
        )}

        {activeTab === "recruitment" && (
          <div className="chart-box full-width">
            <h3>Recruitment Funnel</h3>
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={recruitment}
                  dataKey="count"
                  nameKey="stage"
                  cx="50%"
                  cy="50%"
                  outerRadius={130}
                  label={(entry) => `${entry.stage}: ${entry.count}`}
                >
                  {recruitment.map((entry, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === "skill-gaps" && (
          <div className="table-box">
            <h3>Employees with Skill Gaps</h3>
            <table>
              <thead>
                <tr><th>Employee ID</th><th>Department</th><th>Gap Count</th></tr>
              </thead>
              <tbody>
                {skillGaps.map((row, i) => (
                  <tr key={i}>
                    <td>{row.employee_id}</td>
                    <td>{row.department}</td>
                    <td><span className="badge">{row.gap_count}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "alerts" && (
          <div className="alerts-list">
            <h3>Alert Center ({openAlerts.length} open)</h3>
            {alerts.map(alert => (
              <div key={alert.id} className={`alert-card severity-${alert.severity.toLowerCase()}`}>
                <div className="alert-header">
                  <span className="alert-type">{alert.alert_type}</span>
                  <span className={`severity-badge severity-${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                  <span className={`status-badge status-${alert.status.toLowerCase()}`}>{alert.status}</span>
                </div>
                <p className="alert-reason">{alert.trigger_reason}</p>
                <div className="alert-footer">
                  <span>Owner: {alert.owner}</span>
                  {alert.employee_id && <span> | Employee: {alert.employee_id}</span>}
                  {alert.department && <span> | Dept: {alert.department}</span>}
                  {alert.status === "Open" && (
                    <button className="ack-btn" onClick={() => acknowledgeAlert(alert.id)}>
                      Acknowledge
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

      </main>
    </div>
  );
}

export default App;