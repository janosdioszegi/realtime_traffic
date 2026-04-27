import csv
import psycopg2
import glob
import os
import sys
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = sys.argv[1]
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

cur = conn.cursor()

files = glob.glob(os.path.join(DATA_DIR, "processed_*.csv"))

if not files:
    print("No processed files found.")
    exit()

latest_file = max(files, key=os.path.getctime)

print("Loading:", latest_file)

with open(latest_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute("""
            INSERT INTO traffic_flow (
                road,
                speed,
                free_flow,
                jam_factor,
                congestion_index,
                confidence,
                measurement_time
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (road, measurement_time) DO NOTHING
        """, (
            row["road"],
            float(row["speed"]),
            float(row["free_flow"]),
            float(row["jam_factor"]),
            float(row["congestion_index"]),
            float(row["confidence"]),
            row["measurement_time"]
        ))

conn.commit()
cur.close()
conn.close()

print("Load completed ✔")