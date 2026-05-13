
import json
import time
import pandas as pd
from datetime import datetime
from kafka import KafkaProducer

# Load REAL patient data
df = pd.read_csv('data/icu_patient_data.csv')

# Take first 10 real patients for streaming
real_patients = df.head(10)[['patient_id', 'age', 'heart_rate_mean', 'temperature_mean', 'spo2_mean']].copy()

print("=" * 60)
print("KAFKA PRODUCER - STREAMING REAL ICU PATIENT DATA")
print("=" * 60)
print(f"Loaded {len(real_patients)} REAL patients from dataset")
print(f"Data source: icu_patient_data.csv (15,000 total patients)")
print("=" * 60)

# Connect to Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

message_count = 0

try:
    while True:
        for index, patient in real_patients.iterrows():
            # Use REAL vital signs from dataset
            message = {
                "patient_id": f"REAL-{patient['patient_id']}",
                "age": int(patient['age']),
                "heart_rate": float(patient['heart_rate_mean']),
                "temperature": float(patient['temperature_mean']),
                "spo2": float(patient['spo2_mean']),
                "timestamp": datetime.now().isoformat(),
                "data_source": "MIMIC-III Real ICU Data",
                "event_id": f"real_evt_{int(time.time())}_{patient['patient_id']}"
            }
            
            # Send to Kafka
            producer.send("patient-vitals", message)
            message_count += 1
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Patient {message['patient_id']} | "
                  f"Age:{message['age']} | HR:{message['heart_rate']:.0f} | "
                  f"Temp:{message['temperature']:.1f}°C | SpO2:{message['spo2']:.0f}%")
            
            time.sleep(5)  # Send every 5 seconds
            
except KeyboardInterrupt:
    print(f"\n\n✅ Producer stopped. Sent {message_count} real patient records.")
    producer.close()
