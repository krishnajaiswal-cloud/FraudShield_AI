#!/usr/bin/env python3
"""
FraudShield AI - Database Reset Utility

Purpose: Safely reset development database while preserving schema
Features:
- Delete all test data from analyses, findings, reports
- Reset auto-increment counters
- Show record counts before/after
- Safe transaction handling
- Comprehensive error handling
- Production-quality logging

Usage:
    python scripts/reset_database.py
    python scripts/reset_database.py --backup
    python scripts/reset_database.py --force
    python scripts/reset_database.py --verify
"""

import sqlite3
import logging
import sys
import argparse
from pathlib import Path
from datetime import datetime
import shutil

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get backend directory (where this script's parent is scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
DB_PATH = BACKEND_DIR / "data" / "fraudshield.db"
BACKUP_DIR = BACKEND_DIR / "data" / "backups"

# Table order for deletion (respecting foreign key constraints)
DELETE_ORDER = [
    "chat_histories",    # No dependencies (plural form)
    "findings",          # Depends on analyses
    "reports",           # Depends on analyses
    "analyses",          # Root table
]

# Auto-increment tables
SEQUENCE_TABLES = ["analyses", "findings", "reports", "chat_histories"]

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    """Configure logging for database operations"""
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(BACKEND_DIR / "logs" / "database_reset.log")
        ]
    )
    return logging.getLogger("database_reset")

logger = setup_logging()

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def verify_database_exists():
    """Verify database file exists"""
    if not DB_PATH.exists():
        logger.error(f"Database not found: {DB_PATH}")
        return False
    logger.info(f"Database found: {DB_PATH}")
    return True

def connect_to_database():
    """Establish safe database connection"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        logger.info("Connected to database")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def get_record_counts(conn):
    """Get current record counts for all tables"""
    cursor = conn.cursor()
    counts = {}
    
    tables = ["analyses", "findings", "reports", "chat_histories"]
    
    try:
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            counts[table] = count
        
        logger.info("Record counts retrieved")
        return counts
    except sqlite3.Error as e:
        logger.error(f"Failed to get record counts: {e}")
        raise

def display_counts(counts, phase="Current"):
    """Display record counts in formatted table"""
    print(f"\n{phase} Record Counts:")
    print("=" * 50)
    print(f"  Analyses:     {counts.get('analyses', 0):>5} records")
    print(f"  Findings:     {counts.get('findings', 0):>5} records")
    print(f"  Reports:      {counts.get('reports', 0):>5} records")
    print(f"  Chat Histories: {counts.get('chat_histories', 0):>5} records")
    print("=" * 50)
    total = sum(counts.values())
    print(f"  TOTAL:        {total:>5} records")
    print("=" * 50)

def create_backup():
    """Create backup of current database"""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"fraudshield_backup_{timestamp}.db"
        
        logger.info(f"Creating backup: {backup_path}")
        shutil.copy2(str(DB_PATH), str(backup_path))
        logger.info(f"Backup created successfully")
        return backup_path
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return None

def delete_records(conn):
    """Delete all records from tables in proper order"""
    cursor = conn.cursor()
    deleted_counts = {}
    
    try:
        # Disable foreign key constraints temporarily for cleanup
        cursor.execute("PRAGMA foreign_keys = OFF")
        logger.info("Foreign key constraints disabled for cleanup")
        
        for table in DELETE_ORDER:
            try:
                cursor.execute(f"DELETE FROM {table}")
                deleted_counts[table] = cursor.rowcount
                logger.info(f"Deleted {cursor.rowcount} records from {table}")
            except sqlite3.Error as e:
                logger.error(f"Failed to delete from {table}: {e}")
                raise
        
        # Re-enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        logger.info("Foreign key constraints re-enabled")
        
        return deleted_counts
    except sqlite3.Error as e:
        logger.error(f"Error during deletion: {e}")
        raise

def reset_sequences(conn):
    """Reset SQLite auto-increment counters"""
    cursor = conn.cursor()
    
    try:
        # Check if sqlite_sequence table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            logger.info("sqlite_sequence table doesn't exist yet (no auto-increments used)")
            return True
        
        # Delete all entries from sqlite_sequence
        cursor.execute("DELETE FROM sqlite_sequence")
        deleted = cursor.rowcount
        logger.info(f"Deleted {deleted} entries from sqlite_sequence")
        
        # Verify sqlite_sequence is empty
        cursor.execute("SELECT COUNT(*) FROM sqlite_sequence")
        remaining = cursor.fetchone()[0]
        
        if remaining == 0:
            logger.info("Auto-increment counters successfully reset")
            return True
        else:
            logger.warning(f"Warning: {remaining} entries remain in sqlite_sequence")
            return False
    except sqlite3.Error as e:
        logger.error(f"Failed to reset sequences: {e}")
        raise

def verify_cleanup(conn):
    """Verify all data was deleted successfully"""
    cursor = conn.cursor()
    
    try:
        logger.info("Verifying cleanup...")
        
        for table in ["analyses", "findings", "reports", "chat_histories"]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            
            if count == 0:
                logger.info(f"[OK] {table}: Verified empty")
                print(f"  ✓ {table}: Verified empty")
            else:
                logger.warning(f"[WARN] {table}: Still contains {count} records")
                return False
        
        logger.info("Cleanup verification successful")
        return True
    except sqlite3.Error as e:
        logger.error(f"Verification failed: {e}")
        raise

def reset_database(backup=True, force=False):
    """Main database reset function"""
    try:
        # Step 1: Verify database exists
        print("\n" + "=" * 70)
        print("FraudShield AI - Database Reset Utility")
        print("=" * 70)
        
        if not verify_database_exists():
            return False
        
        # Step 2: Connect to database
        conn = connect_to_database()
        
        # Step 3: Show initial record counts
        logger.info("Retrieving initial record counts...")
        initial_counts = get_record_counts(conn)
        display_counts(initial_counts, "Initial")
        
        # Check if there's data to delete
        total_records = sum(initial_counts.values())
        if total_records == 0:
            print("\n✓ Database is already clean - no data to delete")
            logger.info("Database already clean")
            conn.close()
            return True
        
        # Step 4: Confirm operation
        if not force:
            print(f"\n⚠ WARNING: This will delete {total_records} records")
            confirmation = input("Continue with database reset? (yes/no): ").strip().lower()
            if confirmation != "yes":
                print("✗ Reset cancelled")
                logger.info("Reset cancelled by user")
                conn.close()
                return False
        
        # Step 5: Create backup if requested
        if backup:
            backup_path = create_backup()
            if backup_path:
                print(f"✓ Backup created: {backup_path}")
        
        # Step 6: Begin transaction
        print("\nResetting database...")
        logger.info("Starting reset transaction")
        
        # Step 7: Delete records
        deleted_counts = delete_records(conn)
        print(f"✓ Deleted {sum(deleted_counts.values())} total records")
        
        # Step 8: Reset auto-increment counters
        reset_sequences(conn)
        print("✓ Auto-increment counters reset")
        
        # Step 9: Commit transaction
        conn.commit()
        logger.info("Reset transaction committed")
        print("✓ Transaction committed")
        
        # Step 10: Verify cleanup
        if verify_cleanup(conn):
            print("✓ Cleanup verified")
        else:
            logger.error("Cleanup verification failed")
            print("✗ Cleanup verification failed")
            conn.close()
            return False
        
        # Step 11: Show final record counts
        final_counts = get_record_counts(conn)
        display_counts(final_counts, "Final")
        
        # Step 12: Close connection
        conn.close()
        logger.info("Database connection closed")
        
        # Step 13: Success message
        print("\n" + "=" * 70)
        print("✓ DATABASE RESET COMPLETE")
        print("=" * 70)
        print(f"Analyses:       {final_counts.get('analyses', 0)}")
        print(f"Findings:       {final_counts.get('findings', 0)}")
        print(f"Reports:        {final_counts.get('reports', 0)}")
        print(f"Chat Histories: {final_counts.get('chat_histories', 0)}")
        print("=" * 70 + "\n")
        
        logger.info("Database reset completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Reset failed: {e}", exc_info=True)
        print(f"\n✗ ERROR: {e}")
        return False

# ============================================================================
# VERIFICATION UTILITIES
# ============================================================================

def verify_schema(verbose=False):
    """Verify database schema is intact"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        print("\n" + "=" * 70)
        print("Database Schema Verification")
        print("=" * 70)
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("✗ No tables found in database")
            return False
        
        print(f"\n✓ Found {len(tables)} tables:\n")
        
        for (table_name,) in tables:
            # Get column count
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            print(f"  • {table_name:<20} - {len(columns):>2} columns, {row_count:>6} rows")
            
            if verbose:
                for col in columns:
                    col_id, name, type_, notnull, default, pk = col
                    pk_marker = " [PK]" if pk else ""
                    print(f"      - {name:<25} {type_:<15}{pk_marker}")
        
        # Get indexes
        cursor.execute("""
            SELECT name, tbl_name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name
        """)
        indexes = cursor.fetchall()
        
        if indexes:
            print(f"\n✓ Found {len(indexes)} indexes:\n")
            for index_name, tbl_name in indexes:
                print(f"  • {index_name:<30} on {tbl_name}")
        
        print("\n" + "=" * 70)
        print("✓ Schema verification complete")
        print("=" * 70 + "\n")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Schema verification failed: {e}")
        print(f"✗ Error: {e}")
        return False

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="FraudShield AI - Database Reset Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/reset_database.py           # Reset with backup (interactive)
  python scripts/reset_database.py --force   # Reset without confirmation
  python scripts/reset_database.py --verify  # Verify schema only
  python scripts/reset_database.py --backup  # Create backup only
        """
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt"
    )
    
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup without reset (dry-run)"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify schema only (no reset)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation"
    )
    
    args = parser.parse_args()
    
    # Handle --verify flag
    if args.verify:
        return verify_schema(verbose=args.verbose)
    
    # Handle --backup flag (backup only)
    if args.backup:
        print("\n" + "=" * 70)
        print("Creating backup only (no reset)")
        print("=" * 70)
        backup_path = create_backup()
        if backup_path:
            print(f"✓ Backup created: {backup_path}\n")
            return True
        else:
            print("✗ Backup failed\n")
            return False
    
    # Handle main reset operation
    backup_enabled = not args.no_backup
    result = reset_database(backup=backup_enabled, force=args.force)
    
    return result

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user")
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
