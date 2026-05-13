
import json
import psycopg2
from datetime import datetime
from kafka import KafkaConsumer
import threading

print("=" * 60)
print("PHASE 6: DATABASE STORAGE SERVICE")
print("=" * 60)

# Create PostgreSQL connection
try:
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("✅ Connected to PostgreSQL")
except:
    print("⚠️ PostgreSQL not running. Creating SQLite fallback...")
    import sqlite3
    conn = sqlite3.connect('icu_alerts.db')
    cur = conn.cursor()
    print("✅ Using SQLite database")

# Create tables
cur.execute("""
    CREATE TABLE IF NOT EXISTS patient_alerts (
        id SERIAL PRIMARY KEY,
        patient_id TEXT,
        heart_rate REAL,
        temperature REAL,
        spo2 REAL,
        risk_score INTEGER,
        risk_level TEXT,
        alert_time TIMESTAMP
    )
""")

cur.execute("""
    CREATE TABLE IF NOT EXISTS system_metrics (
        id SERIAL PRIMARY KEY,
        metric_name TEXT,
        metric_value REAL,
        recorded_time TIMESTAMP
    )
""")
print("✅ Tables created")

# Kafka consumer for predictions
def consume_and_store():
    try:
        consumer = KafkaConsumer(
            'predictions',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='latest',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        count = 0
        for message in consumer:
            data = message.value
            cur.execute("""
                INSERT INTO patient_alerts (patient_id, heart_rate, temperature, spo2, risk_score, risk_level, alert_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('patient_id'),
                data.get('heart_rate'),
                data.get('temperature'),
                data.get('spo2'),
                data.get('risk_score'),
                data.get('risk_level'),
                datetime.now()
            ))
            conn.commit()
            count += 1
            if count % 10 == 0:
                print(f"📊 Stored {count} predictions in database")
                
    except Exception as e:
        print(f"Consumer error: {e}")

# Start consumer thread
thread = threading.Thread(target=consume_and_store, daemon=True)
thread.start()
print("✅ Listening to predictions topic...")
print("-" * 60)

# Keep running
try:
    import time
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n✅ Stopped. Data stored in database.")
    conn.close()
