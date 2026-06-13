"""Systematic database debugging - gather evidence"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("STEP 1: DATABASE CONFIGURATION")
print("=" * 80)

# Get configured values
from app.core.config import settings
print(f"\n1. DATABASE_URL (from settings):")
print(f"   {settings.DATABASE_URL}")

print(f"\n2. Resolved URL (from get_database_url()):")
resolved_url = settings.get_database_url()
print(f"   {resolved_url}")

print(f"\n3. Extract file path:")
if "sqlite:///" in resolved_url:
    file_path = resolved_url.replace("sqlite:///", "").replace("/", "\\")
    print(f"   {file_path}")
else:
    file_path = None
    print(f"   ERROR: Cannot extract path from {resolved_url}")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 2: DATABASE FILE STATUS")
print("=" * 80)

if file_path:
    db_file = Path(file_path)
    print(f"\n1. Exists: {db_file.exists()}")
    if db_file.exists():
        print(f"   Yes - {db_file}")
        print(f"2. Size: {db_file.stat().st_size} bytes")
    else:
        print(f"   No - File not found at {db_file}")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 3: SQLAlchemy ENGINE STATUS")
print("=" * 80)

from app.database.database import engine
print(f"\n1. Engine URL: {engine.url}")
print(f"2. Pool class: {engine.pool.__class__.__name__}")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 4: DIRECT SQLITE CONNECTION")
print("=" * 80)

import sqlite3
if file_path and Path(file_path).exists():
    try:
        print(f"\n1. Connecting to: {file_path}")
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print(f"\n2. Tables in database:")
        if tables:
            for table in tables:
                print(f"   - {table[0]}")
            
            # Check for required tables
            table_names = [t[0] for t in tables]
            required = ['analyses', 'findings', 'reports', 'chat_histories']
            missing = [t for t in required if t not in table_names]
            
            if missing:
                print(f"\n3. MISSING TABLES: {', '.join(missing)}")
            else:
                print(f"\n3. ALL REQUIRED TABLES PRESENT")
        else:
            print("   NO TABLES FOUND - Database is empty!")
        
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("File does not exist, cannot connect")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 5: FIND ALL SQLITE FILES IN PROJECT")
print("=" * 80)

backend_path = Path(__file__).parent
print(f"\nSearching in: {backend_path}")

sqlite_files = list(backend_path.rglob("*.db"))
print(f"\nFound {len(sqlite_files)} SQLite files:")
for db in sorted(sqlite_files):
    size = db.stat().st_size
    print(f"  - {db.relative_to(backend_path)}")
    print(f"    Size: {size} bytes")
    print(f"    Full path: {db}")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 6: CHECK BASE.METADATA")
print("=" * 80)

from app.database.base import Base
print(f"\n1. Base.metadata.tables:")
if Base.metadata.tables:
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"   - {table_name}")
else:
    print("   NO TABLES DEFINED IN BASE.METADATA")

print(f"\n2. Total tables defined: {len(Base.metadata.tables)}")

# ============================================================================
print("\n" + "=" * 80)
print("STEP 7: CHECK IF MODELS ARE IMPORTED")
print("=" * 80)

try:
    from app.database.models import Analysis, Finding, Report, ChatHistory
    print("\n1. Models imported successfully")
    print(f"   - Analysis: {Analysis}")
    print(f"   - Finding: {Finding}")
    print(f"   - Report: {Report}")
    print(f"   - ChatHistory: {ChatHistory}")
    
    print(f"\n2. Base.metadata.tables after import:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"   - {table_name}")
except Exception as e:
    print(f"ERROR importing models: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
