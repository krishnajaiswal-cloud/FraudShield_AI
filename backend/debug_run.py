import requests
import hashlib
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"
apk_path = "./app/storage/uploads/test_sample.apk"

# Get the latest analysis
response = requests.get(f"{API_BASE}/analysis?limit=1")
data = response.json()
analysis_id = data["items"][0]["id"]
print(f"Latest Analysis ID: {analysis_id}")

# Get full details
response = requests.get(f"{API_BASE}/analysis/{analysis_id}")
data = response.json()
print(f"\nAnalysis Details:")
print(f"  Status: {data['status']}")
print(f"  Error Message: {data.get('error_message', 'None')}")
print(f"  Threat Type: {data.get('threat_type')}")

# Try to run analysis
print(f"\nAttempting to run analysis {analysis_id}...")
response = requests.post(f"{API_BASE}/analysis/{analysis_id}/run")
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
