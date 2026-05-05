import requests
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import sys

load_dotenv()

PROJECT_ROOT = sys.argv[1]
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY missing from .env")

BBOX = "18.682251,47.008353,19.566650,47.825142"

URL = "https://data.traffic.hereapi.com/v7/flow"

params = {
    "in": f"bbox:{BBOX}",
    "apiKey": API_KEY,
    "locationReferencing": "shape"
}

try:
    response = requests.get(URL, params=params, timeout=(3, 10))
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print("API request failed:", e)
    exit()

data = response.json()

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
file_path = os.path.join(DATA_DIR, f"raw_{timestamp}.json")

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Saved: {file_path}")