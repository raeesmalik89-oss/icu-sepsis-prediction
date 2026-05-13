
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from datetime import datetime
from kafka import KafkaConsumer
import threading
import uvicorn

app = FastAPI(title="ICU Monitoring Dashboard", version="1.0.0")

# Store latest patient data
patients_data = {}
alerts_history = []

# Background thread to consume Kafka predictions
def consume_predictions():
    try:
        consumer = KafkaConsumer(
            'predictions',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        for message in consumer:
            data = message.value
            patient_id = data.get('patient_id', 'Unknown')
            patients_data[patient_id] = data
            if data.get('alert', False):
                alerts_history.append(data)
                # Keep only last 100 alerts
                if len(alerts_history) > 100:
                    alerts_history.pop(0)
    except Exception as e:
        print(f"Kafka consumer error: {e}")

# Start Kafka consumer thread
thread = threading.Thread(target=consume_predictions, daemon=True)
thread.start()

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.get("/")
async def get_dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ICU Patient Monitor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f0f0f0;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .dashboard {
                max-width: 1400px;
                margin: 0 auto;
            }
            .alerts-section {
                background-color: #ffebee;
                border: 2px solid #ef9a9a;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
            }
            .alerts-title {
                color: #c62828;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .alert-item {
                background-color: white;
                border-left: 4px solid red;
                padding: 10px;
                margin: 5px 0;
                font-family: monospace;
            }
            .patients-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .patient-card {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .critical {
                border-left: 5px solid red;
                background-color: #ffebee;
            }
            .moderate {
                border-left: 5px solid orange;
                background-color: #fff3e0;
            }
            .low {
                border-left: 5px solid green;
            }
            .patient-id {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 10px;
            }
            .vital {
                margin: 5px 0;
                font-size: 14px;
            }
            .risk-badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            .risk-critical { background-color: red; color: white; }
            .risk-moderate { background-color: orange; color: white; }
            .risk-low { background-color: green; color: white; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <h1>🏥 ICU Real-Time Patient Monitor</h1>
            <div class="alerts-section">
                <div class="alerts-title">🚨 CRITICAL ALERTS</div>
                <div id="alerts-list">Loading...</div>
            </div>
            <div id="patients-grid" class="patients-grid">Loading patients...</div>
        </div>
        <script>
            let ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                let data = JSON.parse(event.data);
                updateDashboard(data);
            };
            
            function updateDashboard(data) {
                if (data.type === 'alert') {
                    let alertsDiv = document.getElementById('alerts-list');
                    alertsDiv.innerHTML = '<div class="alert-item">🚨 ' + data.patient_id + ' - Risk: ' + data.risk_level + ' (Score: ' + data.risk_score + ')</div>' + alertsDiv.innerHTML;
                    if (alertsDiv.children.length > 10) {
                        alertsDiv.removeChild(alertsDiv.lastChild);
                    }
                } else if (data.type === 'patient_update') {
                    renderPatients();
                }
            }
            
            function renderPatients() {
                let container = document.getElementById('patients-grid');
                // Simplified - actual implementation would fetch from API
            }
            
            setInterval(() => {
                fetch('/api/patients')
                    .then(res => res.json())
                    .then(data => {
                        let container = document.getElementById('patients-grid');
                        container.innerHTML = '';
                        for (let [id, patient] of Object.entries(data)) {
                            let cardClass = 'patient-card';
                            if (patient.risk_level === 'CRITICAL') cardClass += ' critical';
                            else if (patient.risk_level === 'MODERATE') cardClass += ' moderate';
                            else cardClass += ' low';
                            
                            let riskClass = 'risk-critical';
                            if (patient.risk_level === 'MODERATE') riskClass = 'risk-moderate';
                            if (patient.risk_level === 'LOW') riskClass = 'risk-low';
                            
                            container.innerHTML += `
                                <div class="${cardClass}">
                                    <div class="patient-id">${id}</div>
                                    <div class="vital">❤️ Heart Rate: ${patient.heart_rate} bpm</div>
                                    <div class="vital">🌡️ Temperature: ${patient.temperature}°C</div>
                                    <div class="vital">🫁 SpO2: ${patient.spo2}%</div>
                                    <div><span class="risk-badge ${riskClass}">${patient.risk_level}</span> Score: ${patient.risk_score}</div>
                                </div>
                            `;
                        }
                    });
            }, 3000);
        </script>
    </body>
    </html>
    """)

@app.get("/api/patients")
async def get_patients():
    return patients_data

@app.get("/api/alerts")
async def get_alerts():
    return alerts_history[-20:]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
