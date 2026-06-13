"""Start application and test POST /api/v1/analysis"""
import subprocess
import time
import requests
import json
import sys

print("=" * 80)
print("STARTING APPLICATION")
print("=" * 80)

# Start application
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=r"C:\Users\Krishna Jaiswal\OneDrive\Desktop\PSB\FraudShield-AI\backend",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print("Waiting for app to start...")
time.sleep(5)

print("\n" + "=" * 80)
print("TESTING HEALTH ENDPOINT")
print("=" * 80)

try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("TESTING POST /api/v1/analysis")
print("=" * 80)

payload = {
    "apk_name": "test.apk",
    "package_name": "com.test.app",
    "file_path": "/path/to/test.apk",
    "file_hash": "abcd1234",
    "md5_hash": "1234abcd",
    "version_name": "1.0.0",
    "version_code": "1",
    "app_name": "Test App"
}

try:
    response = requests.post(
        "http://localhost:8000/api/v1/analysis",
        json=payload,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 80)
print("TERMINATING APPLICATION")
print("=" * 80)

proc.terminate()
time.sleep(2)
proc.kill()

print("Done")
