#!/usr/bin/env python3
"""
FraudShield AI - Database Diagnostic Script

Comprehensive database diagnostics including:
- Database file location and integrity
- Connection configuration
- Table schema validation
- Row counts and indices
- Performance metrics
- Common issues detection
"""

import os
import sys
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to path (move up one level from scripts/)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("FRAUDSHIELD AI - DATABASE DIAGNOSTIC REPORT")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}\n")

# ============================================================================
# SECTION 1: ENVIRONMENT AND CONFIGURATION
# ============================================================================

print("1. ENVIRONMENT CONFIGURATION")
print("-" * 80)

try:
    from app.core.config import settings
    print(f"[OK] Settings imported successfully")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Debug Mode: {settings.DEBUG}")
    print(f"  DATABASE_URL: {settings.DATABASE_URL}")
    
    db_url = settings.get_database_url()
    print(f"  Resolved URL: {db_url}")
    
    # Check if using in-memory database
    if ":memory:" in db_url:
        print(f"  [WARN] WARNING: Using IN-MEMORY database! Data will not persist.")
        print(f"         This is expected for testing only.")
    
except Exception as e:
    print(f"[FAIL] Failed to import settings: {e}")
    sys.exit(1)

# ============================================================================
# SECTION 2: DATABASE FILE VALIDATION
# ============================================================================

print("\n2. DATABASE FILE VALIDATION")
print("-" * 80)

# Extract file path from URL
if "sqlite:///" in db_url:
    db_path = Path(db_url.replace("sqlite:///", "").replace("\\", "/"))
elif ":memory:" in db_url:
    print("  [INFO] Using in-memory database (no file)")
    db_path = None
else:
    print(f"[FAIL] Unrecognized database URL format: {db_url}")
    db_path = None

if db_path:
    # Resolve to absolute path
    if not db_path.is_absolute():
        # Relative path - resolve from backend directory
        backend_dir = Path(__file__).parent
        db_path = backend_dir / db_path
    
    print(f"Database path: {db_path}")
    print(f"Absolute path: {db_path.absolute()}")
    
    if db_path.exists():
        size_bytes = os.path.getsize(db_path)
        size_kb = size_bytes / 1024
        print(f"[OK] File exists")
        print(f"  Size: {size_bytes:,} bytes ({size_kb:.1f} KB)")
        print(f"  Created: {datetime.fromtimestamp(os.path.getctime(db_path))}")
        print(f"  Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
    else:
        print(f"[FAIL] File NOT found")
        print(f"  Expected location: {db_path.absolute()}")

# ============================================================================
# SECTION 3: DATABASE CONNECTIVITY
# ============================================================================

print("\n3. DATABASE CONNECTIVITY")
print("-" * 80)

try:
    from app.database.database import engine, SessionLocal
    print(f"[OK] Engine created successfully")
    print(f"  Pool: {engine.pool.__class__.__name__}")
    print(f"  Echo: {engine.echo}")
    
    # Try to get a connection
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print(f"[OK] Database connection successful")
    except Exception as e:
        print(f"[FAIL] Connection test failed: {e}")
        
except Exception as e:
    print(f"[FAIL] Failed to create engine: {e}")
    sys.exit(1)

# ============================================================================
# SECTION 4: TABLE SCHEMA VALIDATION
# ============================================================================

print("\n4. TABLE SCHEMA VALIDATION")
print("-" * 80)

try:
    # Get SQLAlchemy inspector
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"Tables found: {len(tables)}")
    
    expected_tables = {
        'analyses': ['id', 'package_name', 'app_name', 'status'],
        'findings': ['id', 'analysis_id', 'threat_type'],
        'reports': ['id', 'analysis_id', 'report_json'],
        'chat_histories': ['id', 'analysis_id', 'message'],
    }
    
    found_tables = {}
    missing_tables = []
    
    for table_name, expected_columns in expected_tables.items():
        if table_name in tables:
            found_tables[table_name] = True
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            print(f"\n  [OK] {table_name}")
            print(f"    Columns: {', '.join(column_names)}")
            
            # Check for expected columns
            missing_cols = [col for col in expected_columns if col not in column_names]
            if missing_cols:
                print(f"    [WARN] Missing expected columns: {', '.join(missing_cols)}")
            
            # Get primary key
            pk = inspector.get_pk_constraint(table_name)
            if pk['constrained_columns']:
                print(f"    Primary Key: {', '.join(pk['constrained_columns'])}")
            
            # Get indices
            indices = inspector.get_indexes(table_name)
            if indices:
                print(f"    Indices: {len(indices)}")
                for idx in indices:
                    print(f"      - {idx['name']}: {', '.join(idx['column_names'])}")
        else:
            missing_tables.append(table_name)
            print(f"  [FAIL] {table_name} - NOT FOUND")
    
    if missing_tables:
        print(f"\n  [WARN] MISSING TABLES: {', '.join(missing_tables)}")
        print(f"         Database schema may not be initialized!")
    else:
        print(f"\n  [OK] All expected tables present")
        
except Exception as e:
    print(f"[FAIL] Schema validation failed: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SECTION 5: DATA CONTENT INSPECTION
# ============================================================================

print("\n5. DATA CONTENT INSPECTION")
print("-" * 80)

try:
    db = SessionLocal()
    
    if ":memory:" in db_url:
        print("  [INFO] Skipping (in-memory database)")
    else:
        # Count rows in each table
        tables_stats = {}
        for table_name in expected_tables.keys():
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                tables_stats[table_name] = count
                status = "[OK]" if count >= 0 else "[?]"
                print(f"  {status} {table_name}: {count:,} rows")
            except Exception as e:
                print(f"  [FAIL] {table_name}: Query failed - {str(e)[:50]}")
        
        # Sample data from analyses table if not empty
        try:
            result = db.execute(text("SELECT COUNT(*) FROM analyses"))
            count = result.scalar()
            if count > 0:
                print(f"\n  Latest analyses:")
                result = db.execute(
                    text("SELECT id, package_name, status, created_at FROM analyses ORDER BY created_at DESC LIMIT 3")
                )
                for row in result:
                    print(f"    - ID {row[0]}: {row[1]} ({row[2]}) - {row[3]}")
        except Exception as e:
            pass  # Silent if table empty or doesn't exist
    
    db.close()
    
except Exception as e:
    print(f"[FAIL] Data inspection failed: {e}")

# ============================================================================
# SECTION 6: INITIALIZATION TEST
# ============================================================================

print("\n6. INITIALIZATION TEST")
print("-" * 80)

try:
    from app.database.database import init_db
    
    # Don't actually call init_db() as it would recreate tables
    # Just verify the function exists and is callable
    print(f"[OK] init_db() function exists and is callable")
    print(f"  Location: app.database.database.init_db")
    print(f"  Function: {init_db.__doc__.strip().split(chr(10))[0] if init_db.__doc__ else 'N/A'}")
    
except Exception as e:
    print(f"[FAIL] Failed to verify init_db: {e}")

# ============================================================================
# SECTION 7: COMMON ISSUES DETECTION
# ============================================================================

print("\n7. COMMON ISSUES DETECTION")
print("-" * 80)

issues = []

# Check 1: In-memory database in non-test environment
if ":memory:" in db_url and settings.ENVIRONMENT != "testing":
    issues.append(
        "⚠️  In-memory database detected in non-test environment. "
        "Data will not persist between restarts."
    )

# Check 2: Missing database file
if db_path and not db_path.exists():
    issues.append(
        "❌ Database file does not exist. "
        f"Expected: {db_path.absolute()}"
    )

# Check 3: Missing tables
if 'missing_tables' in locals() and missing_tables:
    issues.append(
        f"❌ Missing database tables: {', '.join(missing_tables)}. "
        "Run init_db() to create tables."
    )

# Check 4: No data (may indicate initialization issue)
if 'tables_stats' in locals():
    total_rows = sum(tables_stats.values())
    if total_rows == 0 and settings.ENVIRONMENT != "testing":
        issues.append(
            "ℹ️  No data in database (empty). This is normal for a fresh installation."
        )

if issues:
    print("Potential issues found:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
else:
    print("[OK] No common issues detected")

# ============================================================================
# SECTION 8: RECOMMENDATIONS
# ============================================================================

print("\n8. RECOMMENDATIONS")
print("-" * 80)

recommendations = []

if "missing_tables" in locals() and missing_tables:
    recommendations.append(
        "Run database initialization:\n"
        "    from app.database.database import init_db\n"
        "    init_db()"
    )

if ":memory:" in db_url and settings.ENVIRONMENT == "development":
    recommendations.append(
        "Switch to file-based database:\n"
        "    Set ENVIRONMENT=development in .env\n"
        "    Or ensure settings.ENVIRONMENT != 'testing'"
    )

if db_path and not db_path.exists():
    recommendations.append(
        f"Create database directory:\n"
        f"    mkdir -p {db_path.parent}"
    )

if recommendations:
    print("Actions to take:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
else:
    print("✓ Database appears to be properly configured")

# ============================================================================
# FOOTER
# ============================================================================

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
