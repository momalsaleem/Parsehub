#!/usr/bin/env python
"""
Sync metadata with project tokens - ensures metadata.project_token is populated
"""
from backend.database import ParseHubDatabase
import sys
sys.path.insert(
    0, 'd:\\Paramount Intelligence\\ParseHub\\Updated POC\\Parsehub_project')


db = ParseHubDatabase()

# First check what projects and metadata we have
db.connect()
cursor = db.conn.cursor()

# Check projects
cursor.execute('SELECT id, token, title FROM projects LIMIT 5')
projects = cursor.fetchall()
print("Sample projects:")
for p in projects:
    print(f"  ID: {p[0]}, Token: {p[1]}, Title: {p[2]}")

# Check metadata
cursor.execute(
    'SELECT id, project_token, project_name, total_pages FROM metadata LIMIT 5')
metadata = cursor.fetchall()
print("\nSample metadata:")
for m in metadata:
    print(f"  ID: {m[0]}, Token: {m[1]}, Name: {m[2]}, Pages: {m[3]}")

# Look for our specific project
cursor.execute(
    'SELECT id, token, title FROM projects WHERE token = ?', ('tsTA0g3nsdNd',))
project = cursor.fetchone()
print(f"\nLooking for project token 'tsTA0g3nsdNd': {project}")

db.disconnect()

# Now sync metadata with projects to populate project_token
print("\nSyncing metadata with projects...")

db.connect()
cursor = db.conn.cursor()

# Get all projects
cursor.execute('SELECT id, token, title FROM projects')
all_projects = cursor.fetchall()

print(f"\nFound {len(all_projects)} projects")

# Try to match metadata to projects
for project_id, token, title in all_projects:
    # Try to find matching metadata by project name
    cursor.execute('''
        SELECT id FROM metadata 
        WHERE project_name = ? AND project_token IS NULL
        LIMIT 1
    ''', (title,))

    metadata_id = cursor.fetchone()
    if metadata_id:
        # Update the metadata with the project token
        cursor.execute('''
            UPDATE metadata 
            SET project_token = ?, project_id = ?
            WHERE id = ?
        ''', (token, project_id, metadata_id[0]))
        print(f"Updated metadata for project '{title}' (token: {token})")

db.conn.commit()
db.disconnect()

print("Sync complete!")
