#!/usr/bin/env python3
"""Test frontend API calls to verify filtered results display properly"""
import requests
import json

# Simulate what the frontend does when user selects a website filter

BASE_URL = "http://localhost:3000"  # Frontend API route
API_BACKEND = "http://localhost:5000"  # Backend

print("\n" + "="*70)
print("FRONTEND FILTER TEST")
print("="*70)

# 1. Get available filters (this is what shows in the filter dropdowns)
print("\n1. Fetching available filters...")
response = requests.get(f"{BASE_URL}/api/filters")
if response.status_code == 200:
    filters = response.json().get('filters', {})
    websites = filters.get('websites', [])
    print(f"   ✅ Got {len(websites)} websites")
    print(f"   Sample: {websites[:3]}")
else:
    print(f"   ❌ Failed to get filters: {response.status_code}")

# 2. Simulate user selecting a website filter
print("\n2. Simulating user selecting 'Filter-technik.de' website filter...")
print("   Frontend would call: /api/projects?website=Filter-technik.de&limit=50&page=1")

response = requests.get(
    f"{BASE_URL}/api/projects",
    params={
        "website": "Filter-technik.de",
        "limit": 50,
        "page": 1
    }
)

if response.status_code == 200:
    data = response.json()

    # Check the response structure
    print(f"\n   ✅ Got response from frontend API")
    print(f"   Response keys: {list(data.keys())}")

    # Check projects
    projects = data.get('projects', [])
    by_website = data.get('by_website', [])

    print(f"\n   Projects in response: {len(projects)}")
    print(f"   Website groups: {len(by_website)}")

    # Verify all projects are Filter-technik.de
    websites_in_projects = set()
    for proj in projects:
        w = proj.get('website', 'Unknown')
        websites_in_projects.add(w)

    print(f"   Unique websites in projects: {websites_in_projects}")

    # Check if filtering worked
    if len(websites_in_projects) == 1 and 'filter-technik.de' in websites_in_projects:
        print(f"\n   ✅ FILTERING WORKS: Only 'filter-technik.de' projects returned!")

        # Show sample
        print(f"\n   Sample projects (first 3):")
        for proj in projects[:3]:
            print(f"      - {proj.get('title', 'Unknown')[:70]}")
    else:
        print(
            f"\n   ❌ FILTERING FAILED: Got multiple websites {websites_in_projects}")
else:
    print(f"   ❌ Failed: HTTP {response.status_code}")
    print(f"   Response: {response.text[:200]}")

print("\n" + "="*70)
