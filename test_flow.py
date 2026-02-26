#!/usr/bin/env python
import requests
import time

print('Testing full pagination flow...\n')

for page in range(1, 4):
    print(f'=== Page {page} ===')

    try:
        start = time.time()
        response = requests.get(
            f'http://localhost:3000/api/projects?page={page}&limit=20', timeout=15)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            proj_count = data.get('project_count', 0)
            page_info = data.get('pagination', {})
            total_pages = page_info.get('total_pages', 0)
            total_projects = page_info.get('total', 0)

            print(f'✓ Page {page}/{total_pages} (total: {total_projects})')
            print(f'  Time: {elapsed:.3f}s | Projects on page: {proj_count}')

            if proj_count > 0:
                print(
                    f'  Sample: {data.get("projects", [{}])[0].get("title", "N/A")[:50]}')
        else:
            print(f'✗ Status: {response.status_code}')
            print(f'  Response: {response.text[:100]}')
    except Exception as e:
        print(f'✗ Error: {str(e)[:80]}')

    if page < 3:
        print()
        time.sleep(0.5)

print('\n✅ Pagination test complete!')
