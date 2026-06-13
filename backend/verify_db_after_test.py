"""Verify database tables exist after successful API test"""
import sqlite3
import os

db_path = r"C:\Users\Krishna Jaiswal\OneDrive\Desktop\PSB\FraudShield-AI\backend\data\fraudshield.db"

if os.path.exists(db_path):
    print(f"Database file exists: {db_path}")
    print(f"File size: {os.path.getsize(db_path)} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\nTables in database: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
        # Get row count for each table
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
    
    conn.close()
else:
    print(f"Database file NOT found: {db_path}")
