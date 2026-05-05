import json
import os
import csv
import sys
from datetime import datetime
import zoneinfo

PROJECT_ROOT = sys.argv[1]
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


def get_latest_file():
    files = os.listdir(DATA_DIR)
    files = [f for f in files if f.startswith("raw_") and f.endswith(".json")]

    if not files:
        raise ValueError(f"No raw files found in {DATA_DIR}")

    latest = max(files)
    return os.path.join(DATA_DIR, latest)


def transform(data):
    rows = []

    for item in data.get("results", []):

        location_obj = item.get("location", {})
        description = location_obj.get("description")

        if not description:
            continue

        flow = item.get("currentFlow", {})

        speed = flow.get("speed")
        free_flow = flow.get("freeFlow")
        jam_factor = flow.get("jamFactor")
        confidence = flow.get("confidence")

        if speed is None or free_flow is None:
            continue

        shape = location_obj.get("shape", {})
        links = shape.get("links", [])

        if not links:
            continue

        for link in links:

            points = link.get("points", [])
            if len(points) < 2:
                continue

            start = points[0]
            end = points[-1]

            rows.append({
                "road": description,

                "speed": speed,
                "free_flow": free_flow,
                "jam_factor": jam_factor,
                "congestion_index": jam_factor,
                "confidence": confidence,

                "start_lat": start.get("lat"),
                "start_lng": start.get("lng"),
                "end_lat": end.get("lat"),
                "end_lng": end.get("lng"),

                "segment_length": link.get("length"),

                "measurement_time": datetime.now(
                    zoneinfo.ZoneInfo("Europe/Budapest")
                )
            })

    return rows


file_path = get_latest_file()
print("Processing:", file_path)

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = transform(data)

if not rows:
    print("No valid rows, skipping.")
    exit()

timestamp = datetime.now(
    zoneinfo.ZoneInfo("Europe/Budapest")
).strftime("%Y%m%d_%H%M%S")

output_file = os.path.join(DATA_DIR, f"processed_{timestamp}.csv")

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Saved:", output_file)