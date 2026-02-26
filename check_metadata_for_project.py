#!/usr/bin/env python
"""
Check metadata for specific project
"""
from backend.database import ParseHubDatabase
import sys
sys.path.insert(
    0, 'd:\\Paramount Intelligence\\ParseHub\\Updated POC\\Parsehub_project')


db = ParseHubDatabase()
db.connect()
cursor = db.conn.cursor()

# Find the project
cursor.execute(
    'SELECT id, token, title FROM projects WHERE token = ?', ('tsTA0g3nsdNd',))
project = cursor.fetchone()

if project:
    project_id, token, title = project
    print(f"Found project:")
    print(f"  ID: {project_id}")
    print(f"  Token: {token}")
    print(f"  Title: {title}")
    print()

    # Look for metadata with matching token
    cursor.execute(
        'SELECT id, project_token, project_name, total_pages FROM metadata WHERE project_token = ?', (token,))
    metadata_by_token = cursor.fetchall()
    print(f"Metadata with matching project_token: {len(metadata_by_token)}")
    for m in metadata_by_token:
        print(f"  {m}")
    print()

    # Look for metadata with matching name
    cursor.execute(
        'SELECT id, project_token, project_name, total_pages FROM metadata WHERE project_name LIKE ?', (f"%{title}%",))
    metadata_by_name = cursor.fetchall()
    print(f"Metadata with matching project_name: {len(metadata_by_name)}")
    for m in metadata_by_name:
        print(f"  {m}")
    print()

    # List all metadata without a project_token
    cursor.execute(
        'SELECT id, project_token, project_name, total_pages FROM metadata WHERE project_token IS NULL LIMIT 10')
    unlinked = cursor.fetchall()
    print(f"Sample unlinked metadata (project_token IS NULL): {len(unlinked)}")
    for m in unlinked:
        print(f"  {m}")

db.disconnect()
