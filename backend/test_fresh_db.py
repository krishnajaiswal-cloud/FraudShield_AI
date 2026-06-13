"""Delete database and restart app to test initialization"""
import subprocess
import time
import os
import requests
import sys

db_path = r"C:\Users\Krishna Jaiswal\OneDrive\Desktop\PSB\FraudShield-AI\backend\data\fraudshield.db"

print("=" * 80)
print("CLEANING UP DATABASE")
print("=" * 80)

# Wait for previous process to release file
time.sleep(2)

if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✓ Deleted database: {db_path}")
    except Exception as e:
        print(f"✗ Could not delete: {e}")
else:
    print(f"Database not found at {db_path}")

print("\n" + "=" * 80)
print("STARTING APPLICATION (FRESH)")
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
print("TESTING POST /api/v1/analysis (FRESH DATABASE)")
print("=" * 80)

payload = {
    "apk_name": "test.apk",
    "package_name": "com.test.app",
    "file_path": "/path/to/test.apk",
    "file_hash": "xyz789",
    "md5_hash": "789xyz",
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
    if response.status_code == 201:
        print("✓ SUCCESS - Record created in fresh database")
        print(f"Response: {response.json()}")
    else:
        print(f"✗ FAILED - Status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n" + "=" * 80)
print("CHECKING DATABASE STATE")
print("=" * 80)

import sqlite3
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"✓ Tables created: {len(tables)}")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} rows")
    conn.close()
else:
    print(f"✗ Database file not found")

print("\n" + "=" * 80)
print("TERMINATING APPLICATION")
print("=" * 80)

proc.terminate()
time.sleep(2)
proc.kill()

print("Done")
