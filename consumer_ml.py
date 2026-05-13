
import json
import joblib
import pandas as pd
from datetime import datetime
from kafka import KafkaConsumer

# Load trained model
try:
    model = joblib.load('models/best_model.pkl')
    print("✅ Model loaded successfully")
except:
    print("⚠️ Model not found, using rule-based prediction")
    model = None

print("=" * 60)
print("KAFKA CONSUMER - REAL-TIME SEPSIS PREDICTION")
print("=" * 60)
print("Listening to topic: patient-vitals")
print("Press Ctrl+C to stop")
print("=" * 60)

# Connect to Kafka
consumer = KafkaConsumer(
    'patient-vitals',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def predict_sepsis_risk(heart_rate, temperature, spo2):
    """Simple rule-based risk prediction"""
    risk_score = 0
    
    # High heart rate (>100 bpm)
    if heart_rate > 100:
        risk_score += 2
    
    # Fever (>38.3°C)
    if temperature > 38.3:
        risk_score += 2
    
    # Low oxygen (<92%)
    if spo2 < 92:
        risk_score += 2
    
    if risk_score >= 4:
        return "🔴 CRITICAL", risk_score
    elif risk_score >= 2:
        return "🟡 MODERATE", risk_score
    else:
        return "🟢 LOW", risk_score

message_count = 0
alerts = 0

try:
    for message in consumer:
        data = message.value
        message_count += 1
        
        heart_rate = data.get('heart_rate', 0)
        temperature = data.get('temperature', 0)
        spo2 = data.get('spo2', 0)
        patient_id = data.get('patient_id', 'Unknown')
        
        # Predict risk
        risk_level, risk_score = predict_sepsis_risk(heart_rate, temperature, spo2)
        
        if risk_level == "🔴 CRITICAL":
            alerts += 1
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {patient_id} | "
              f"HR:{heart_rate:.0f} | Temp:{temperature:.1f}°C | SpO2:{spo2:.0f}% | "
              f"Risk:{risk_level} (Score:{risk_score})")
        
        # Critical alert
        if risk_level == "🔴 CRITICAL":
            print(f"  🚨 ALERT: Patient {patient_id} requires immediate attention!")
            
except KeyboardInterrupt:
    print(f"\n\n" + "=" * 60)
    print(f"SUMMARY")
    print("=" * 60)
    print(f"Total messages processed: {message_count}")
    print(f"Critical alerts triggered: {alerts}")
    print(f"Alert rate: {alerts/message_count*100:.1f}%")
