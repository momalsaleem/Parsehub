#!/usr/bin/env python3
"""
Check runs table schema
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "backend" / "parsehub.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get columns in runs table
cursor.execute("PRAGMA table_info(runs)")
columns = cursor.fetchall()

print("RUNS TABLE COLUMNS:")
for col in columns:
    print(f"  • {col[1]} ({col[2]})")

# Get first row
cursor.execute("SELECT * FROM runs LIMIT 1")
row = cursor.fetchone()

if row:
    print("\nFirst row in runs table:")
    for i, col in enumerate(columns):
        col_name = col[1]
        print(f"  {col_name}: {row[i]}")

conn.close()
