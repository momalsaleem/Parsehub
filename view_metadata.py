"""
Quick script to view metadata from the database
Usage: python view_metadata.py
"""
import sqlite3
import json
from pathlib import Path
from database_config import DATABASE_PATH

db_path = DATABASE_PATH
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

print("=" * 80)
print("METADATA TABLE - ALL RECORDS")
print("=" * 80)

cursor = conn.cursor()
cursor.execute("""
    SELECT personal_project_id, project_name, region, country, brand, 
           project_id, project_token, website_url, created_at
    FROM metadata
    ORDER BY CAST(personal_project_id AS INTEGER)
""")

rows = cursor.fetchall()
for i, row in enumerate(rows, 1):
    print(f"\n--- Record {i} ---")
    for key in row.keys():
        value = row[key]
        if key == 'website_url' and value and len(value) > 60:
            value = value[:60] + "..."
        print(f"  {key}: {value}")

print(f"\n{'=' * 80}")
print(f"Total Records: {len(rows)}")

# Summary statistics
cursor.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(project_token) as with_token,
        COUNT(DISTINCT region) as regions,
        COUNT(DISTINCT country) as countries,
        COUNT(DISTINCT brand) as brands
    FROM metadata
""")
stats = dict(cursor.fetchone())
print(f"\nSummary:")
print(f"  Total metadata records: {stats['total']}")
print(f"  Linked to projects: {stats['with_token']}")
print(f"  Regions: {stats['regions']}")
print(f"  Countries: {stats['countries']}")
print(f"  Brands: {stats['brands']}")

conn.close()
