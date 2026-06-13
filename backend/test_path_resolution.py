"""Quick test of absolute path resolution"""
from app.core.config import settings
from app.database.database import engine
import sqlite3

print("Testing absolute path resolution:")
print(f"  Resolved URL: {settings.get_database_url()}")
print(f"  Engine URL: {engine.url}")

# Verify tables exist with the resolved path
db_url = settings.get_database_url()
db_path = db_url.replace("sqlite:///", "").replace("/", "\\")
if db_path.startswith("C:"):  # Windows absolute path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  Tables found: {tables}")
    conn.close()
