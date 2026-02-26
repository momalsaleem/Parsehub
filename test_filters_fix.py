#!/usr/bin/env python
import requests
import time

print('=== Testing Updated Frontend with Filters ===\n')

# Test 1: Default view (50 per page)
print('Test 1: Default view (50 per page)')
try:
    start = time.time()
    r = requests.get(
        'http://localhost:3000/api/projects?page=1&limit=50', timeout=15)
    elapsed = time.time() - start

    if r.status_code == 200:
        data = r.json()
        count = data.get('project_count', 0)
        total = data.get('pagination', {}).get('total', 0)
        print(
            f'✓ Status: 200 - Time: {elapsed:.3f}s - Showing: {count} / Total: {total}\n')
    else:
        print(f'✗ Status: {r.status_code}\n')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}\n')

# Test 2: All projects mode (1000/all)
print('Test 2: All projects mode (limit 1000)')
try:
    start = time.time()
    r = requests.get(
        'http://localhost:3000/api/projects?page=1&limit=1000', timeout=15)
    elapsed = time.time() - start

    if r.status_code == 200:
        data = r.json()
        count = data.get('project_count', 0)
        print(
            f'✓ Status: 200 - Time: {elapsed:.3f}s - Total projects: {count}\n')
    else:
        print(f'✗ Status: {r.status_code}\n')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}\n')

# Test 3: Filters - by region
print('Test 3: Filter by region (if available)')
try:
    # First get available filters
    r = requests.get('http://localhost:3000/api/filters', timeout=10)
    if r.status_code == 200:
        data = r.json()
        regions = data.get('filters', {}).get('regions', [])
        if regions:
            test_region = regions[0]
            print(f'  Testing with region: {test_region}')

            start = time.time()
            r2 = requests.get(
                f'http://localhost:3000/api/projects?page=1&limit=50&region={test_region}', timeout=15)
            elapsed = time.time() - start

            if r2.status_code == 200:
                data2 = r2.json()
                count = data2.get('project_count', 0)
                total = data2.get('pagination', {}).get('total', 0)
                print(
                    f'✓ Filter works! - Time: {elapsed:.3f}s - Results: {count} / Total filtered: {total}\n')
            else:
                print(f'✗ Status: {r2.status_code}\n')
        else:
            print('  No regions available to test\n')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}\n')

# Test 4: Check filters are visible
print('Test 4: Filters available (Region, Country, Brand, Website)')
try:
    r = requests.get('http://localhost:3000/api/filters', timeout=10)
    if r.status_code == 200:
        data = r.json()
        regions = len(data.get('filters', {}).get('regions', []))
        countries = len(data.get('filters', {}).get('countries', []))
        brands = len(data.get('filters', {}).get('brands', []))
        websites = len(data.get('filters', {}).get('websites', []))

        print(f'✓ Filters loaded:')
        print(f'  Regions: {regions}')
        print(f'  Countries: {countries}')
        print(f'  Brands: {brands}')
        print(f'  Websites: {websites}\n')
    else:
        print(f'✗ Status: {r.status_code}\n')
except Exception as e:
    print(f'✗ Error: {str(e)[:80]}\n')

print('=== All tests complete ===')
