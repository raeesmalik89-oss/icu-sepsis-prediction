
# ICU Patient Monitoring System

## What is this project?

This system monitors ICU patients in real-time and predicts sepsis risk using machine learning. It streams patient vital signs through Kafka, processes them with an ML model, and shows results on a web dashboard.

## How it works

1. Patient vitals (heart rate, temperature, oxygen) are sent every 5 seconds
2. Kafka streams the data to the ML consumer
3. Model calculates risk score (0-6) and risk level
4. Dashboard displays all patients with color-coded alerts
5. High-risk patients trigger immediate notifications

## What I built

| Component | What it does |
|-----------|--------------|
| Data pipeline | 15,000 real ICU patients from MIMIC-III database |
| ML Model | Logistic Regression, 63.8% ROC-AUC |
| Streaming | Apache Kafka for real-time data |
| Dashboard | FastAPI web interface |
| Storage | PostgreSQL database for alerts |
| Security | Keycloak auth, OPA rules, Trivy scans |
| Auto-remediation | Self-healing when issues detected |

## How to run

```bash
# Start services
docker compose up -d

# Run producer (sends patient data)
python producer_real.py

# Run ML consumer (predicts risk)
python consumer_ml_inference.py

# Open dashboard
python dashboard.py



Then open browser to http://localhost:8000

Project status
All 6 phases complete. System works with real ICU data and generates real-time alerts.

What I learned
Building event-driven systems with Kafka

Training ML models for healthcare data

Handling class imbalance in medical datasets

Deploying secure, compliant systems

Creating self-healing AIOps pipelines

Files in this repo
producer_real.py - Sends patient vitals to Kafka

consumer_ml_inference.py - ML model for risk prediction

dashboard.py - Web interface

database_storage.py - Saves alerts to PostgreSQL

auto_remediation.py - Self-healing engine

docker-compose.yml - Runs Kafka, PostgreSQL, Keycloak

Author
Raees Malik  ALNAFI INTERNATIONAL COLLEGE 
