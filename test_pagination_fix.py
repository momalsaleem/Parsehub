"""
Test script to verify the paginated /api/projects endpoint
Measures response time and pagination functionality
"""

import requests
import time
import json
from datetime import datetime

# Backend URL
BACKEND_URL = 'http://localhost:5000'
API_KEY = 'b70fe8b04c26431590efaba99c0b6a4d'  # Your API key


def test_paginated_endpoint():
    """Test the new paginated /api/projects endpoint"""

    print("\n" + "="*70)
    print("🧪 Testing Paginated /api/projects Endpoint")
    print("="*70)

    tests = [
        {'page': 1, 'limit': 20, 'description': 'First page (20 items)'},
        {'page': 2, 'limit': 20, 'description': 'Second page (20 items)'},
        {'page': 1, 'limit': 10, 'description': 'First page (10 items)'},
        {'page': 1, 'limit': 50, 'description': 'First page (50 items - max)'},
        {'page': 1, 'limit': 20, 'filter_keyword': 'youtube',
            'description': 'Filter by "youtube"'},
        {'page': 1, 'limit': 20, 'filter_keyword': 'ecommerce',
            'description': 'Filter by "ecommerce"'},
    ]

    for test in tests:
        params = {'api_key': API_KEY}
        params['page'] = test['page']
        params['limit'] = test['limit']
        if 'filter_keyword' in test:
            params['filter_keyword'] = test['filter_keyword']

        print(f"\n📋 Test: {test['description']}")
        print(f"   Parameters: {params}")

        try:
            start_time = time.time()
            response = requests.get(
                f'{BACKEND_URL}/api/projects', params=params, timeout=60)
            elapsed = time.time() - start_time

            print(f"   ⏱️  Response time: {elapsed:.2f}s")
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                pagination = data.get('pagination', {})
                projects = data.get('projects', [])

                print(f"   ✅ Response OK")
                print(f"   - Total projects: {pagination.get('total', 'N/A')}")
                print(
                    f"   - Page: {pagination.get('page', 'N/A')}/{pagination.get('total_pages', 'N/A')}")
                print(f"   - Items on this page: {len(projects)}")
                print(f"   - Has more: {pagination.get('has_more', False)}")
                print(
                    f"   - Metadata matches: {data.get('metadata_matches', 0)}")

                if projects:
                    print(
                        f"   - Sample project: {projects[0].get('title', 'N/A')[:50]}")
            else:
                print(f"   ❌ Error: {response.text}")

        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")


def test_bulk_endpoint():
    """Test the /api/projects/bulk endpoint"""

    print("\n" + "="*70)
    print("🧪 Testing Bulk /api/projects/bulk Endpoint")
    print("="*70)

    params = {'api_key': API_KEY}

    print(f"\n📋 Fetching all projects at once...")
    print(f"   Parameters: {params}")

    try:
        start_time = time.time()
        response = requests.get(
            f'{BACKEND_URL}/api/projects/bulk', params=params, timeout=300)
        elapsed = time.time() - start_time

        print(f"   ⏱️  Response time: {elapsed:.2f}s")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])

            print(f"   ✅ Bulk fetch complete")
            print(f"   - Total projects: {data.get('total', 'N/A')}")
            print(f"   - Projects in response: {len(projects)}")
            print(f"   - Metadata matches: {data.get('metadata_matches', 0)}")
            print(f"   - Website groups: {len(data.get('by_website', []))}")

            # Show timing comparison
            print(
                f"\n   📊 Timing: Bulk took {elapsed:.2f}s for {len(projects)} projects")
            if len(projects) > 0:
                per_project = elapsed / len(projects)
                print(f"      Average: {per_project:.3f}s per project")
        else:
            print(f"   ❌ Error: {response.text}")

    except requests.Timeout:
        print(f"   ⏱️  Request timeout (300s)")
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")


def test_comparison():
    """Compare paginated vs bulk performance"""

    print("\n" + "="*70)
    print("📊 Performance Comparison")
    print("="*70)

    # Time a single paginated request
    print("\n1️⃣  Paginated endpoint (page 1, 20 items):")
    try:
        start = time.time()
        response = requests.get(
            f'{BACKEND_URL}/api/projects',
            params={'api_key': API_KEY, 'page': 1, 'limit': 20},
            timeout=60
        )
        paginated_time = time.time() - start
        print(f"   ✅ Time: {paginated_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        paginated_time = None

    # Time bulk endpoint
    print("\n2️⃣  Bulk endpoint (all projects):")
    try:
        start = time.time()
        response = requests.get(
            f'{BACKEND_URL}/api/projects/bulk',
            params={'api_key': API_KEY},
            timeout=300
        )
        bulk_time = time.time() - start
        print(f"   ✅ Time: {bulk_time:.2f}s")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        bulk_time = None

    if paginated_time and bulk_time:
        speedup = bulk_time / paginated_time
        print(f"\n📈 Speedup: Paginated is {speedup:.1f}x faster than bulk")


if __name__ == '__main__':
    print(
        f"\n🚀 Starting tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")

    test_paginated_endpoint()

    # Uncomment to test bulk endpoint
    # test_bulk_endpoint()

    # Uncomment to compare performance
    # test_comparison()

    print(
        f"\n✅ Tests completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
