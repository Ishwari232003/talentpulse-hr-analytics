import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

employee_ids = [f"EMP{i:04d}" for i in range(1, 701)]
statuses = ["Present", "Absent", "Half-Day", "Leave", "WFH"]

print("Starting attendance event producer... (Ctrl+C to stop)")

event_count = 0
while True:
    event = {
        "employee_id": random.choice(employee_ids),
        "date": datetime.today().strftime("%Y-%m-%d"),
        "status": random.choices(statuses, weights=[80, 5, 5, 5, 5])[0],
        "hours": 8,
        "event_time": datetime.now().isoformat()
    }
    event["hours"] = 8 if event["status"] == "Present" else (4 if event["status"] == "Half-Day" else 0)

    producer.send("attendance-events", value=event)
    event_count += 1
    print(f"[{event_count}] Sent: {event}")

    time.sleep(2)  # send one event every 2 seconds