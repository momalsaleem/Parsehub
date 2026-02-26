#!/usr/bin/env python
"""
Check all metadata in database
"""
from backend.database import ParseHubDatabase
import sys
sys.path.insert(
    0, 'd:\\Paramount Intelligence\\ParseHub\\Updated POC\\Parsehub_project')


db = ParseHubDatabase()
db.connect()
cursor = db.conn.cursor()

# Count all metadata
cursor.execute('SELECT COUNT(*) FROM metadata')
total = cursor.fetchone()[0]
print(f"Total metadata records: {total}")

# Count metadata with project_token
cursor.execute('SELECT COUNT(*) FROM metadata WHERE project_token IS NOT NULL')
with_token = cursor.fetchone()[0]
print(f"Metadata with project_token: {with_token}")

# Count metadata without project_token
cursor.execute('SELECT COUNT(*) FROM metadata WHERE project_token IS NULL')
without_token = cursor.fetchone()[0]
print(f"Metadata without project_token: {without_token}")

# Check projects
cursor.execute('SELECT COUNT(*) FROM projects')
total_projects = cursor.fetchone()[0]
print(f"\nTotal projects: {total_projects}")

# Sample metadata records
cursor.execute(
    'SELECT id, project_token, project_name, total_pages, personal_project_id FROM metadata ORDER BY id DESC LIMIT 20')
results = cursor.fetchall()
print(f"\nLatest 20 metadata records:")
for row in results:
    print(
        f"  ID: {row[0]}, Token: {row[1]}, Name: {row[2]}, Pages: {row[3]}, PersonalID: {row[4]}")

db.disconnect()
