"""Quick diagnostic script to check database status"""
import sqlite3
import os
from pathlib import Path

db_path = Path('./data/fraudshield.db')

print("=" * 60)
print("DATABASE DIAGNOSTIC REPORT")
print("=" * 60)

# Check if file exists
if db_path.exists():
    print(f"\n✓ Database file exists: {db_path.absolute()}")
    print(f"  Size: {os.path.getsize(db_path)} bytes")
else:
    print(f"\n✗ Database file NOT found: {db_path.absolute()}")
    exit(1)

# Connect and check tables
try:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\nTables found: {len(tables)}")
    if tables:
        for table_name in tables:
            table = table_name[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            print(f"  ✓ {table} ({row_count} rows)")
    else:
        print("  ✗ NO TABLES FOUND - Database is empty!")
    
    # Check schema for expected tables
    expected_tables = ['analyses', 'findings', 'reports', 'chat_histories']
    missing = []
    for table in expected_tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            missing.append(table)
    
    if missing:
        print(f"\n✗ MISSING TABLES: {', '.join(missing)}")
    else:
        print(f"\n✓ All required tables present")
    
    conn.close()
    
except Exception as e:
    print(f"\n✗ Error reading database: {e}")
    exit(1)

print("\n" + "=" * 60)
