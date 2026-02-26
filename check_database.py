import sqlite3
from pathlib import Path

db_path = Path("backend/parsehub.db")

print("Checking database for synced projects...")
print("="*60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check total projects
cursor.execute("SELECT COUNT(*) FROM projects")
total = cursor.fetchone()[0]
print(f"\nTotal projects in database: {total}")

# Get first 10 projects
cursor.execute("SELECT id, token, title, owner_email FROM projects LIMIT 10")
projects = cursor.fetchall()

print(f"\nFirst 10 projects:")
print("-"*60)
for project in projects:
    print(f"ID: {project[0]}")
    print(f"Token: {project[1]}")
    print(f"Title: {project[2]}")
    print(f"Owner: {project[3]}")
    print("-"*60)

# Search for the specific project
token = "tq3KfpOZe-d6"
cursor.execute(
    "SELECT id, token, title FROM projects WHERE token = ?", (token,))
result = cursor.fetchone()

if result:
    print(f"\n✅ Found project with token {token}")
    print(f"ID: {result[0]}, Title: {result[2]}")
else:
    print(f"\n❌ Project with token {token} not found in database")

    # Search for similar tokens
    cursor.execute(
        "SELECT token, title FROM projects WHERE token LIKE ?", (f"%{token[:8]}%",))
    similar = cursor.fetchall()

    if similar:
        print(f"\nSimilar tokens found:")
        for sim in similar:
            print(f"  {sim[0]} - {sim[1]}")

conn.close()
print("\n" + "="*60)
