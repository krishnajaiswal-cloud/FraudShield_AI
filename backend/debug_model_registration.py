"""Detailed model registration debugging"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("STEP 1: CHECK BASE BEFORE IMPORT")
print("=" * 80)

from app.database.database import Base as DatabaseBase
print(f"\nBase object: {DatabaseBase}")
print(f"Base.metadata: {DatabaseBase.metadata}")
print(f"Tables: {list(DatabaseBase.metadata.tables.keys())}")

print("\n" + "=" * 80)
print("STEP 2: IMPORT MODELS")
print("=" * 80)

print("\nImporting Analysis...")
from app.database.models import Analysis
print(f"  Analysis class: {Analysis}")
print(f"  Analysis.__tablename__: {getattr(Analysis, '__tablename__', 'NOT DEFINED')}")
print(f"  Analysis.__bases__: {Analysis.__bases__}")
print(f"  Is subclass of Base: {issubclass(Analysis, DatabaseBase)}")

print(f"\nBase.metadata.tables: {list(DatabaseBase.metadata.tables.keys())}")

print("\nImporting Finding...")
from app.database.models import Finding
print(f"  Finding class: {Finding}")
print(f"  Finding.__tablename__: {getattr(Finding, '__tablename__', 'NOT DEFINED')}")
print(f"  Is subclass of Base: {issubclass(Finding, DatabaseBase)}")

print(f"\nBase.metadata.tables: {list(DatabaseBase.metadata.tables.keys())}")

print("\nImporting Report...")
from app.database.models import Report
print(f"  Report class: {Report}")
print(f"  Report.__tablename__: {getattr(Report, '__tablename__', 'NOT DEFINED')}")
print(f"  Is subclass of Base: {issubclass(Report, DatabaseBase)}")

print(f"\nBase.metadata.tables: {list(DatabaseBase.metadata.tables.keys())}")

print("\nImporting ChatHistory...")
from app.database.models import ChatHistory
print(f"  ChatHistory class: {ChatHistory}")
print(f"  ChatHistory.__tablename__: {getattr(ChatHistory, '__tablename__', 'NOT DEFINED')}")
print(f"  Is subclass of Base: {issubclass(ChatHistory, DatabaseBase)}")

print(f"\nBase.metadata.tables: {list(DatabaseBase.metadata.tables.keys())}")

print("\n" + "=" * 80)
print("STEP 3: FINAL CHECK")
print("=" * 80)

print(f"\nTotal tables in Base.metadata: {len(DatabaseBase.metadata.tables)}")
for table_name, table_obj in DatabaseBase.metadata.tables.items():
    print(f"  - {table_name}: {table_obj}")

# Try to list table columns
print("\n" + "=" * 80)
print("STEP 4: CHECK TABLE STRUCTURE")
print("=" * 80)

if 'analyses' in DatabaseBase.metadata.tables:
    table = DatabaseBase.metadata.tables['analyses']
    print(f"\nAnalyses table columns:")
    for col in table.columns:
        print(f"  - {col.name}: {col.type}")

# Now try init_db
print("\n" + "=" * 80)
print("STEP 5: CALL init_db()")
print("=" * 80)

from app.database.database import init_db, engine
print(f"\nCalling init_db()...")
try:
    init_db()
    print("SUCCESS: init_db() completed")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

# Check database file
print("\n" + "=" * 80)
print("STEP 6: CHECK ACTUAL DATABASE FILE")
print("=" * 80)

import sqlite3
db_path = "C:\\Users\\Krishna Jaiswal\\OneDrive\\Desktop\\PSB\\FraudShield-AI\\backend\\data\\fraudshield.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables in SQLite file:")
if tables:
    for table in tables:
        print(f"  - {table[0]}")
else:
    print("  NO TABLES")
conn.close()

print("\n" + "=" * 80)
