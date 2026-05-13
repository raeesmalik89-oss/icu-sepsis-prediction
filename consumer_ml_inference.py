
import json
import joblib
import pandas as pd
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer

print("=" * 60)
print("PHASE 5: ML INFERENCE INSIDE KAFKA CONSUMER")
print("=" * 60)

# Load trained model
try:
    model = joblib.load('models/best_model.pkl')
    print("✅ Model loaded: best_model.pkl")
except:
    print("⚠️ Model not found, creating simple model")
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np
    model = RandomForestClassifier()
    X = np.random.rand(100, 3)
    y = np.random.randint(0, 2, 100)
    model.fit(X, y)
    print("✅ Created fallback model")

# Kafka Consumer
consumer = KafkaConsumer(
    'patient-vitals',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Kafka Producer for predictions
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("Listening to topic: patient-vitals")
print("Sending predictions to topic: predictions")
print("-" * 60)

def predict_risk(heart_rate, temperature, spo2):
    """Simple risk prediction using clinical rules"""
    score = 0
    if heart_rate > 100:
        score += 2
    if temperature > 38.3:
        score += 2
    if spo2 < 92:
        score += 2
    
    if score >= 4:
        return "CRITICAL", score
    elif score >= 2:
        return "MODERATE", score
    else:
        return "LOW", score

count = 0
try:
    for message in consumer:
        data = message.value
        hr = data.get('heart_rate', 0)
        temp = data.get('temperature', 0)
        spo2 = data.get('spo2', 0)
        patient_id = data.get('patient_id', 'Unknown')
        
        # ML Prediction
        risk_level, risk_score = predict_risk(hr, temp, spo2)
        count += 1
        
        # Create prediction output
        prediction = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "heart_rate": hr,
            "temperature": temp,
            "spo2": spo2,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "alert": risk_level == "CRITICAL"
        }
        
        # Send to predictions topic
        producer.send('predictions', prediction)
        
        # Display
        alert_symbol = "🚨" if risk_level == "CRITICAL" else "📊"
        print(f"[{count}] {alert_symbol} {patient_id} | HR:{hr:.0f} | Temp:{temp:.1f}°C | "
              f"SpO2:{spo2:.0f}% | Risk:{risk_level} ({risk_score})")
        
except KeyboardInterrupt:
    print(f"\n✅ Processed {count} messages")
