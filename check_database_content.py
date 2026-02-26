#!/usr/bin/env python3
"""
Check what's actually in the database
"""
import sqlite3
import os
from pathlib import Path
from database_config import DATABASE_PATH

DB_PATH = DATABASE_PATH

print("=" * 70)
print("📊 DATABASE CONTENT CHECK")
print("=" * 70)

# Check if DB exists
if not DB_PATH.exists():
    print(f"❌ Database file not found at: {DB_PATH}")
    print(f"   Current directory: {os.getcwd()}")
    print(
        f"   Files in backend/: {os.listdir(Path(__file__).parent / 'backend')}")
    exit(1)

print(f"✅ Database found: {DB_PATH}")
print()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all tables
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("📋 TABLES IN DATABASE:")
print("-" * 70)
if not tables:
    print("❌ NO TABLES FOUND!")
else:
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  • {table_name}: {count} rows")

print()
print("=" * 70)
print("DETAILED TABLE INFORMATION")
print("=" * 70)

for table in tables:
    table_name = table[0]
    print(f"\n📄 TABLE: {table_name}")
    print("-" * 70)

    # Get columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    print("Columns:")
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        print(f"  • {col_name} ({col_type})")

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nRow Count: {count}")

    # Show first 3 rows if data exists
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nFirst {min(3, count)} rows:")
        for i, row in enumerate(rows, 1):
            print(f"  Row {i}: {row}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

# Count total records
total_records = 0
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    total_records += count

print(f"Total records in database: {total_records}")

if total_records == 0:
    print("⚠️  DATABASE IS EMPTY!")
    print("\nPossible causes:")
    print("  1. Ingestion script never ran successfully")
    print("  2. Ingestion script ran but encountered errors")
    print("  3. Data was deleted or database was reset")
    print("\nSolution:")
    print("  1. Check backend logs for errors")
    print("  2. Run ingestion manually:")
    print(
        "     python -c \"import requests; print(requests.post('http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj', params={'days_back': 0}).json())\"")
elif 'product_data' in [t[0] for t in tables]:
    cursor.execute("SELECT COUNT(*) FROM product_data")
    product_count = cursor.fetchone()[0]
    print(f"✅ {product_count} products in database")
else:
    print("⚠️  product_data table doesn't exist!")

print("=" * 70)

conn.close()
