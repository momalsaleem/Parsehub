#!/usr/bin/env python
import requests

print('=== System Health Check ===\n')

# Check backend
try:
    r = requests.get('http://localhost:5000/api/health', timeout=5)
    if r.status_code == 200:
        print('✓ Backend: Running on http://localhost:5000')
    else:
        print('✗ Backend: Not responding correctly')
except:
    print('✗ Backend: Not accessible')

# Check frontend
try:
    r = requests.get('http://localhost:3000/', timeout=5)
    if r.status_code == 200:
        print('✓ Frontend: Running on http://localhost:3000')
    else:
        print('✗ Frontend: Not responding correctly')
except:
    print('✗ Frontend: Not accessible')

# Check pagination endpoint
try:
    r = requests.get(
        'http://localhost:3000/api/projects?page=1&limit=20', timeout=5)
    if r.status_code == 200:
        data = r.json()
        count = data.get('project_count', 0)
        print(f'✓ Pagination: Working ({count} items per page)')
    else:
        print('✗ Pagination: Not working')
except Exception as e:
    print(f'✗ Pagination: Error - {str(e)[:50]}')

print('\n=== Configuration ===')
print('Frontend: http://localhost:3000')
print('Backend: http://localhost:5000')
print('Database: SQLite with WAL mode')
print('Page size: 20 items (configurable)')
print('Cache TTL: 5 minutes')
print('Request timeout: 30 seconds')
