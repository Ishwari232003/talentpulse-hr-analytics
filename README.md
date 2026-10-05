# TalentPulse — HR & Workforce Analytics Platform

An end-to-end data engineering and analytics platform that ingests HR data (batch + real-time streaming), transforms it into business KPIs, automatically detects and alerts on workforce risks, and serves everything through a REST API and a live dashboard.

> Built as an academic capstone project. Runs fully locally via Docker Compose — no cloud deployment in this iteration (see [Scope Notes](#scope-notes)).

---

## What it does

HR teams need answers to questions like *"why is attrition rising,"* *"which recruitment channel costs the most,"* or *"which employees are at risk of leaving"* — but raw data scattered across systems doesn't answer these on its own. TalentPulse ingests employee, recruitment, attendance, learning, performance, exit, and role-change data, cleans and models it into a warehouse, computes 7 core HR KPIs, and runs automated rules that generate real-time alerts (with Slack notifications) when a business condition is triggered — e.g. high attrition risk, a recruitment SLA breach, or an absenteeism anomaly.

## Architecture

```
Source (synthetic CSVs)
        │
        ▼
  Bronze (raw, immutable) ──► Silver / Warehouse (star schema, PostgreSQL)
        ▲                            │
        │                            ├──► Data Quality Checks (10 automated checks)
  Kafka Producer                     │
        │                            ├──► dbt (7 KPI models — Gold layer)
        ▼                            │
  Kafka Consumer                     ├──► Automation Engine (4 rules → alerts + Slack)
        │                            │
        └────────────────────────────┘
                                      ▼
                            FastAPI Backend (REST API)
                                      ▼
                            React Dashboard (frontend)

        Orchestrated end-to-end by Apache Airflow
```

Full diagram and component breakdown: [`docs/architecture.md`](docs/architecture.md)

## Tech stack

| Layer | Technology |
|---|---|
| Data generation | Python, Faker |
| Warehouse | PostgreSQL (star schema: Bronze / Silver / Gold) |
| Streaming | Apache Kafka |
| Transformation | dbt |
| Orchestration | Apache Airflow |
| Automation / alerts | Python, Slack Incoming Webhooks |
| Backend API | FastAPI |
| Frontend | React + Vite, Recharts |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Infrastructure | Docker Compose |

## Key features

- **Bronze → Silver → Gold data architecture**: raw immutable ingestion, cleaned/validated warehouse tables, business-ready KPI views
- **Real-time streaming**: a Kafka producer simulates live attendance events; a consumer processes them into the warehouse within seconds
- **7 dbt-modeled KPIs**: attrition rate, cost-per-hire, time-to-hire, absenteeism, training completion, performance trend, internal mobility
- **Rule-based automation**: 4 business rules continuously evaluated against the warehouse, generating audited alerts with real Slack notifications for high-severity cases
- **10 automated data quality checks**: null, duplicate, uniqueness, referential integrity, business-rule range, freshness, and volume checks, logged for auditability
- **Daily-scheduled orchestration** via an Airflow DAG (load → transform → automate)
- **REST API** with 7 endpoints and auto-generated Swagger docs
- **Live React dashboard**: KPI cards, charts, recruitment funnel, skill-gap table, and an alert center with an acknowledge action
- **Automated testing + CI**: 9 pytest tests, run automatically on every push via GitHub Actions

## Project structure

```
talentpulse/
├── data_generator/       # Synthetic HR data generation (Faker)
├── warehouse/            # SQL schema + batch/bronze loaders
├── streaming/            # Kafka producer & consumer
├── data_quality/         # Automated data quality checks
├── talentpulse_dbt/      # dbt project — 7 KPI models
├── automation/           # Rule-based alerting engine + Slack integration
├── airflow/dags/         # Airflow DAG definition
├── backend/              # FastAPI application
├── frontend/             # React + Vite dashboard
├── tests/                # pytest test suite
├── docs/                 # Architecture diagram, data dictionary, presentation
├── .github/workflows/    # CI/CD pipeline
└── docker-compose.yml    # PostgreSQL, Kafka, Airflow infrastructure
```

## Getting started

**Prerequisites:** Docker Desktop, Python 3.11+, Node.js 20+

```bash
# 1. Start infrastructure (PostgreSQL, Kafka, Airflow)
docker compose up -d

# 2. Set up Python environment
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt   # or install packages individually — see docs

# 3. Generate and load data
cd data_generator && python generate_data.py
cd ../warehouse && python load_data.py && python load_bronze.py

# 4. Build KPIs
cd ../talentpulse_dbt && dbt run

# 5. Run automation (requires SLACK_WEBHOOK_URL in a .env file)
cd ../automation && python run_automation.py

# 6. Start the backend
cd ../backend && uvicorn main:app --reload

# 7. Start the frontend (separate terminal)
cd ../frontend && npm install && npm run dev
```

Then visit:
- Dashboard: http://localhost:5173
- API docs: http://127.0.0.1:8000/docs
- Airflow: http://localhost:8080 (admin/admin)

### Environment variables

Create a `.env` file in the project root:
```
SLACK_WEBHOOK_URL=your_slack_incoming_webhook_url
```

## Testing

```bash
cd tests
pytest test_api.py -v
```

9 tests covering all API endpoints, including error-path handling (404s for invalid IDs).

## Documentation

- [Architecture](docs/architecture.md) — full system diagram and design rationale
- [Data Dictionary](docs/data_dictionary.md) — every table and column, documented
- [Presentation](docs/TalentPulse_Presentation.pptx) — project summary deck

## Scope notes

Per project mentor guidance, two items from the original brief were explicitly descoped:
- **ML/forecasting module** — replaced with 4 transparent, rule-based alert conditions covering the same business triggers (attrition risk, SLA breaches, skill gaps, absenteeism anomalies)
- **Cloud deployment** — the full stack runs locally via Docker Compose; not deployed to a cloud platform in this iteration

All other mandatory deliverables (data warehouse, streaming, dbt, orchestration, automation, API, frontend, testing, CI/CD, documentation) are complete.

## Author

Ishwari Sunagar