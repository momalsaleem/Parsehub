from backend.database import Database

db = Database()
db.connect()
cur = db.connection.cursor()

# Check metadata for this project token
cur.execute('SELECT id, project_token, project_name, total_pages FROM metadata WHERE project_token = ?', ('tsTA0g3nsdNd',))
results = cur.fetchall()
print(f"Metadata with project_token 'tsTA0g3nsdNd': {results}")

# Check all metadata to see what's there
cur.execute(
    'SELECT id, project_token, project_name, total_pages FROM metadata LIMIT 10')
all_results = cur.fetchall()
print(f"\nAll metadata (first 10): {all_results}")

# Check the project details
cur.execute('SELECT id, token, title FROM projects WHERE token = ?',
            ('tsTA0g3nsdNd',))
project = cur.fetchone()
print(f"\nProject: {project}")

db.disconnect()
