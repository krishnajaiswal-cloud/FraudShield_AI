"""Test database initialization"""
import sys
sys.path.insert(0, '.')

from app.database.database import Base, init_db, engine, SessionLocal
from app.database.models import Analysis, Finding, Report, ChatHistory
import sqlite3

print("=" * 60)
print("DATABASE INITIALIZATION TEST")
print("=" * 60)

print("\n1. Engine Configuration:")
print(f"   Engine URL: {engine.url}")
print(f"   Engine Pool: {engine.pool}")

print("\n2. Checking database before init_db():")
conn = sqlite3.connect('./data/fraudshield.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables_before = [t[0] for t in cursor.fetchall()]
print(f"   Tables found: {len(tables_before)}")
for t in sorted(tables_before):
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"     - {t} ({count} rows)")
conn.close()

print("\n3. Calling init_db()...")
try:
    init_db()
    print("   ✓ init_db() succeeded")
except Exception as e:
    print(f"   ✗ init_db() failed: {e}")
    import traceback
    traceback.print_exc()

print("\n4. Checking database after init_db():")
conn = sqlite3.connect('./data/fraudshield.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables_after = [t[0] for t in cursor.fetchall()]
print(f"   Tables found: {len(tables_after)}")
for t in sorted(tables_after):
    cursor.execute(f"SELECT COUNT(*) FROM {t}")
    count = cursor.fetchone()[0]
    print(f"     - {t} ({count} rows)")
conn.close()

print("\n5. Testing SessionLocal connection:")
try:
    db = SessionLocal()
    # Try to query the analyses table
    from sqlalchemy import text
    result = db.execute(text("SELECT COUNT(*) FROM analyses"))
    count = result.scalar()
    print(f"   ✓ Successfully queried analyses table: {count} rows")
    db.close()
except Exception as e:
    print(f"   ✗ Failed to query: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
