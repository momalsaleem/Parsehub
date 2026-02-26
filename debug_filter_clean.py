#!/usr/bin/env python3
"""Debug filtering - check response structure"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test /api/projects/search with website filter
print("\n=== /api/projects/search endpoint ===")
response = requests.get(
    f"{BASE_URL}/api/projects/search",
    params={"website": "Filter-technik.de", "limit": 100}
)

if response.status_code == 200:
    data = response.json()
    print(f"\nResponse keys: {list(data.keys())}")

    # Check what structure is returned
    if 'projects' in data:
        groups = data['projects']  # This is the array of groups
        print(f"Number of website groups: {len(groups)}")

        if groups:
            first_group = groups[0]
            print(f"First group has keys: {list(first_group.keys())}")
            print(f"First group website: {first_group.get('website')}")
            print(
                f"First group projects count: {len(first_group.get('projects', []))}")

            # Show unique websites
            websites_found = {}
            for group in groups:
                w = group.get('website', 'Unknown')
                count = len(group.get('projects', []))
                websites_found[w] = websites_found.get(w, 0) + count

            print(f"\nWebsites found (normalized):")
            for w, count in websites_found.items():
                print(f"  - {w}: {count} projects")

# Also test /api/projects with filters
print("\n\n=== /api/projects endpoint with filters ===")
response = requests.get(
    f"{BASE_URL}/api/projects",
    params={"website": "Filter-technik.de", "limit": 100}
)

if response.status_code == 200:
    data = response.json()
    print(f"\nResponse keys: {list(data.keys())}")
    print(f"Total in response: {data.get('total')}")
    print(f"Project count: {data.get('project_count')}")

    if 'by_website' in data:
        groups = data.get('by_website', [])
        print(f"Number of website groups (by_website): {len(groups)}")
