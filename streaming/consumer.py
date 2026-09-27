import json
import psycopg2
from kafka import KafkaConsumer

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    dbname="talentpulse",
    user="talentpulse",
    password="talentpulse"
)
cur = conn.cursor()

consumer = KafkaConsumer(
    "attendance-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="attendance-consumer-group"
)

print("Consumer started, listening for events... (Ctrl+C to stop)")

for message in consumer:
    event = message.value
    try:
        cur.execute("""
            INSERT INTO fact_attendance (employee_id, date, status, hours)
            VALUES (%s, %s, %s, %s)
        """, (event["employee_id"], event["date"], event["status"], event["hours"]))
        conn.commit()
        print(f"Inserted into Postgres: {event}")
    except Exception as e:
        print(f"Error inserting event: {e}")
        conn.rollback()