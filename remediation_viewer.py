
from kafka import KafkaConsumer
import json

print("=" * 60)
print("REMEDIATION EVENTS VIEWER")
print("=" * 60)
print("Listening to remediation-events topic...")

consumer = KafkaConsumer(
    'remediation-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    event = message.value
    print(f"[{event.get('timestamp')}] Action: {event.get('action')} | Status: {event.get('status')}")
