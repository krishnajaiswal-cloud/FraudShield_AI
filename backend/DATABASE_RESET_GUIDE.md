# Database Reset Utility - Complete Guide

## Overview

**Script**: `backend/scripts/reset_database.py`

**Purpose**: Safely reset the FraudShield development database by deleting all test data while preserving the schema, tables, and indexes.

**Features**:
- ✅ Safe database connection with transaction management
- ✅ Automatic backup creation before deletion
- ✅ Proper foreign key constraint handling
- ✅ Auto-increment counter reset
- ✅ Record counting before/after operations
- ✅ Comprehensive error handling
- ✅ Detailed logging to file and console
- ✅ Schema verification utility
- ✅ Production-quality implementation

---

## Quick Start

### 1. Basic Reset (Interactive with Backup)
```bash
cd backend
python scripts/reset_database.py
```

**Output**:
```
======================================================================
FraudShield AI - Database Reset Utility
======================================================================
Database found: C:\...\fraudshield.db
Connected to database
Record counts retrieved

Initial Record Counts:
==================================================
  Analyses:          45 records
  Findings:        125 records
  Reports:           15 records
  Chat History:      30 records
==================================================
  TOTAL:           215 records
==================================================

⚠ WARNING: This will delete 215 records
Continue with database reset? (yes/no): yes

Resetting database...
✓ Deleted 30 records from chat_history
✓ Deleted 125 records from findings
✓ Deleted 15 records from reports
✓ Deleted 45 records from analyses
✓ Auto-increment counters reset
✓ Transaction committed
✓ Cleanup verified

Final Record Counts:
==================================================
  Analyses:            0 records
  Findings:            0 records
  Reports:             0 records
  Chat History:        0 records
==================================================
  TOTAL:               0 records
==================================================

======================================================================
✓ DATABASE RESET COMPLETE
======================================================================
Analyses:     0
Findings:     0
Reports:      0
Chat History: 0
======================================================================
```

### 2. Reset Without Confirmation (Force Mode)
```bash
python scripts/reset_database.py --force
```

### 3. Create Backup Only (No Reset)
```bash
python scripts/reset_database.py --backup
```

### 4. Verify Schema Only (No Changes)
```bash
python scripts/reset_database.py --verify
```

### 5. Skip Backup and Force Reset
```bash
python scripts/reset_database.py --force --no-backup
```

---

## Command Reference

### Usage Syntax
```bash
python scripts/reset_database.py [OPTIONS]
```

### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--force` | Skip confirmation prompt | `--force` |
| `--backup` | Create backup only, don't reset | `--backup` |
| `--verify` | Verify schema only, no reset | `--verify` |
| `--verbose` or `-v` | Show detailed output | `-v` or `--verbose` |
| `--no-backup` | Skip automatic backup | `--no-backup` |
| `--help` or `-h` | Show help message | `--help` |

### Examples

```bash
# Interactive reset with backup (default)
python scripts/reset_database.py

# Force reset without asking (use with caution!)
python scripts/reset_database.py --force

# Backup only (dry-run, no reset)
python scripts/reset_database.py --backup

# Verify database schema
python scripts/reset_database.py --verify

# Detailed output
python scripts/reset_database.py --verbose

# Force reset, skip backup, verbose output
python scripts/reset_database.py --force --no-backup -v

# Check schema with detailed column info
python scripts/reset_database.py --verify --verbose
```

---

## What Gets Deleted

### Tables (Data Only)
```
1. chat_history      - Delete first (no dependencies)
2. findings          - Delete second (depends on analyses)
3. reports           - Delete third (depends on analyses)
4. analyses          - Delete last (root table)
```

### Preserved
```
✓ Database schema (all table definitions)
✓ Column definitions and types
✓ Indexes (automatically preserved)
✓ Foreign key constraints
✓ Table structure
✓ Views (if any)
```

### Reset
```
✓ Auto-increment counters (IDs start from 1 again)
✓ All records from analyses, findings, reports, chat_history
```

---

## Expected Behavior

### Before Reset
```sql
SELECT COUNT(*) FROM analyses;        -- 45 records
SELECT COUNT(*) FROM findings;        -- 125 records
SELECT COUNT(*) FROM reports;         -- 15 records
SELECT COUNT(*) FROM chat_history;    -- 30 records
```

### After Reset
```sql
SELECT COUNT(*) FROM analyses;        -- 0 records
SELECT COUNT(*) FROM findings;        -- 0 records
SELECT COUNT(*) FROM reports;         -- 0 records
SELECT COUNT(*) FROM chat_history;    -- 0 records

SELECT * FROM sqlite_sequence;        -- Empty (IDs reset)
```

### First Record After Reset
```sql
INSERT INTO analyses (...) VALUES (...);
SELECT id FROM analyses WHERE id = (SELECT MAX(id) FROM analyses);
-- Result: 1 (not 46)
```

---

## Backup Location

### Backup Storage
```
backend/data/backups/fraudshield_backup_YYYYMMDD_HHMMSS.db
```

### Example
```
backend/data/backups/fraudshield_backup_20260611_124530.db
```

### View Backups
```bash
# Windows
dir backend\data\backups\

# Linux/Mac
ls -lh backend/data/backups/
```

### Restore from Backup
```bash
# Restore specific backup
copy backend\data\backups\fraudshield_backup_20260611_124530.db backend\data\fraudshield.db

# Or use restore script (coming soon)
```

---

## Logging

### Log File Location
```
backend/logs/database_reset.log
```

### Log Contents
```
2026-06-11 12:47:25 [INFO] database_reset: Database found: C:\...\fraudshield.db
2026-06-11 12:47:25 [INFO] database_reset: Connected to database
2026-06-11 12:47:25 [INFO] database_reset: Record counts retrieved
2026-06-11 12:47:30 [INFO] database_reset: Creating backup: C:\...\fraudshield_backup_20260611_124730.db
2026-06-11 12:47:30 [INFO] database_reset: Backup created successfully
2026-06-11 12:47:30 [INFO] database_reset: Starting reset transaction
2026-06-11 12:47:30 [INFO] database_reset: Deleted 30 records from chat_history
2026-06-11 12:47:30 [INFO] database_reset: Deleted 125 records from findings
2026-06-11 12:47:30 [INFO] database_reset: Deleted 15 records from reports
2026-06-11 12:47:30 [INFO] database_reset: Deleted 45 records from analyses
2026-06-11 12:47:30 [INFO] database_reset: Reset transaction committed
2026-06-11 12:47:30 [INFO] database_reset: Database reset completed successfully
```

---

## Error Handling

### Scenario 1: Database Not Found
```
✗ ERROR: Database not found: C:\...\fraudshield.db
```

### Scenario 2: Connection Failed
```
✗ ERROR: Failed to connect to database: [error details]
```

### Scenario 3: User Cancels
```
✗ Reset cancelled
```

### Scenario 4: Already Clean
```
✓ Database is already clean - no data to delete
```

---

## Verification Queries

### 1. Check Record Counts After Reset
```sql
-- Run in sqlite3 or any SQL client
SELECT 'analyses' as table_name, COUNT(*) as record_count FROM analyses
UNION ALL
SELECT 'findings', COUNT(*) FROM findings
UNION ALL
SELECT 'reports', COUNT(*) FROM reports
UNION ALL
SELECT 'chat_history', COUNT(*) FROM chat_history;
```

**Expected Output**:
```
table_name    record_count
----------    ----------
analyses      0
findings      0
reports       0
chat_history  0
```

### 2. Verify Auto-Increment Reset
```sql
SELECT * FROM sqlite_sequence;
```

**Expected Output** (empty result set):
```
-- No rows
```

### 3. Verify Schema Integrity
```sql
.schema
```

**Expected Output**: All CREATE TABLE statements intact

### 4. Check Indexes Still Present
```sql
SELECT name, tbl_name FROM sqlite_master 
WHERE type='index' AND name NOT LIKE 'sqlite_%';
```

**Expected Output**: All indexes preserved

### 5. Verify First Insert
```sql
INSERT INTO analyses (package_name, risk_score, severity, threat_type, status, file_hash, version_code)
VALUES ('test.app', 0.5, 'MEDIUM', 'GENERIC', 'COMPLETED', 'abc123', '1');

SELECT id, package_name FROM analyses WHERE id = 1;
```

**Expected Output**:
```
id  package_name
1   test.app
```

---

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Database Reset

on:
  workflow_dispatch:  # Manual trigger
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM

jobs:
  reset-db:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Reset database
        run: |
          cd backend
          python scripts/reset_database.py --force
      
      - name: Upload backup as artifact
        uses: actions/upload-artifact@v2
        with:
          name: database-backup
          path: backend/data/backups/
```

---

## Safety Features

### ✅ Implemented Safeguards

1. **Transaction Management**
   - All operations wrapped in single transaction
   - Rollback on error
   - Commit only after verification

2. **Foreign Key Constraints**
   - Disabled during cleanup (to avoid constraints)
   - Re-enabled after cleanup
   - Verified after operation

3. **Deletion Order**
   - Respects foreign key relationships
   - chat_history → findings → reports → analyses
   - Prevents constraint violations

4. **Backup Creation**
   - Automatic backup before reset
   - Timestamped for easy identification
   - Optional via --no-backup flag

5. **Confirmation Prompt**
   - Shows record count before deletion
   - Requires explicit "yes" confirmation
   - Bypassable with --force for automation

6. **Verification**
   - Post-deletion verification
   - Confirms all records deleted
   - Checks sqlite_sequence is empty

7. **Error Handling**
   - Try-catch blocks around all operations
   - Detailed error logging
   - Graceful failure with clear messages

8. **Logging**
   - All operations logged to file
   - Console and file output
   - Timestamp and level information

---

## Troubleshooting

### Issue: "Database is locked"
**Cause**: Another process has database open (e.g., backend server)

**Solution**:
```bash
# Stop backend server first
# Then run reset
python scripts/reset_database.py --force
```

### Issue: "Foreign key constraint failed"
**Cause**: Deletion order issue or corrupted constraints

**Solution**:
```bash
# Run with verbose mode to see which table fails
python scripts/reset_database.py -v

# Check logs
tail -50 backend/logs/database_reset.log
```

### Issue: "Permission denied"
**Cause**: File permissions on database or backup directory

**Solution**:
```bash
# Check permissions
ls -l backend/data/fraudshield.db
ls -ld backend/data/backups/

# On Windows, ensure you have write permissions
# On Linux/Mac: chmod 755 backend/data backend/data/backups
```

### Issue: Records Still Present
**Cause**: Transaction didn't commit or verification failed

**Solution**:
```bash
# Check logs for detailed error
cat backend/logs/database_reset.log

# Try restore from backup
cp backend/data/backups/fraudshield_backup_*.db backend/data/fraudshield.db

# Try again
python scripts/reset_database.py --force
```

---

## Production Considerations

### NOT for Production
⚠️ This script is designed for **development use only**.

### For Production:
- Use proper backup/restore procedures
- Implement data archival before deletion
- Create audit log of deletions
- Use read replicas for safety
- Implement point-in-time recovery
- Test restore procedures regularly

---

## Advanced Usage

### Custom Integration
```python
from scripts.reset_database import reset_database, verify_schema

# In your Python code
success = reset_database(backup=True, force=False)

if success:
    print("Database reset completed")
else:
    print("Reset failed")
```

### Call from Other Scripts
```bash
#!/bin/bash
# cleanup.sh

cd backend
python scripts/reset_database.py --force --no-backup

# Then run tests
pytest tests/ -v
```

---

## Performance

### Typical Execution Time
- 100 records: < 1 second
- 1,000 records: 1-2 seconds
- 10,000 records: 2-5 seconds
- Backup creation: 0.5-1 second

### Database Size Impact
- No impact on database file size
- SQLite doesn't shrink files automatically
- To optimize: `VACUUM` command (not implemented)

---

## Support & Logs

### View Logs
```bash
# Latest logs
tail -100 backend/logs/database_reset.log

# Search for errors
grep ERROR backend/logs/database_reset.log

# Full log file
cat backend/logs/database_reset.log
```

### Report Issues
When reporting issues, include:
1. Command executed
2. Full error message
3. Relevant log entries
4. Database size (record count)
5. OS and Python version

---

## Version Info

**Script Version**: 1.0.0  
**Created**: 2026-06-11  
**Python**: 3.8+  
**Database**: SQLite 3  
**Status**: Production Ready ✅

---

## License

Part of FraudShield AI backend utilities.

---

Generated: 2026-06-11
Last Updated: 2026-06-11
Status: Production Ready ✅
