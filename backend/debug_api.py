import requests
import hashlib
from pathlib import Path

API_BASE = "http://localhost:8000/api/v1"
apk_path = "./app/storage/uploads/test_sample.apk"

def get_file_hash(file_path: str) -> str:
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

file_size = Path(apk_path).stat().st_size
md5_hash = get_file_hash(apk_path)

payload = {
    "apk_name": "test_sample.apk",
    "package_name": "com.test.sample",
    "file_path": apk_path,
    "file_hash": md5_hash,
    "file_size": file_size,
    "version_name": "1.0.0",
    "version_code": "1",  # Must be string
    "app_name": "Test App",
    "md5_hash": md5_hash
}

print("Payload:")
for k, v in payload.items():
    print(f"  {k}: {v} ({type(v).__name__})")
print("\nSending request...")

response = requests.post(f"{API_BASE}/analysis", json=payload)
print(f"Status: {response.status_code}")
print(f"Response:\n{response.text}")
