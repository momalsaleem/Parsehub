#!/usr/bin/env python3
"""Comprehensive filter testing - verify all filter types work"""
import requests
import json

BASE_URL = "http://localhost:5000"

test_cases = [
    {
        "name": "Test 1: Website filter (Filter-technik.de)",
        "params": {"website": "Filter-technik.de", "limit": 100},
        "expected_websites": ["filter-technik.de"],  # Normalized to lowercase
        "min_projects": 25
    },
    {
        "name": "Test 2: Website filter (aisbelgium.be)",
        "params": {"website": "aisbelgium.be", "limit": 100},
        "expected_websites": ["aisbelgium.be"],
        "min_projects": 1
    },
    {
        "name": "Test 3: Region filter (EMENA)",
        "params": {"region": "EMENA", "limit": 100},
        "expected_regions": ["EMENA"],
        "min_projects": 20
    },
    {
        "name": "Test 4: Country filter (Germany)",
        "params": {"country": "Germany", "limit": 100},
        "expected_countries": ["Germany"],
        "min_projects": 20
    },
]

print("\n" + "="*70)
print("COMPREHENSIVE FILTER TESTS")
print("="*70)

for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print("-" * 70)

    response = requests.get(
        f"{BASE_URL}/api/projects/search",
        params=test_case['params']
    )

    if response.status_code != 200:
        print(f"❌ FAILED: HTTP {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        continue

    data = response.json()

    # Check groups
    groups = data.get('projects', [])
    total_projects = sum(len(g.get('projects', [])) for g in groups)

    if total_projects < test_case.get('min_projects', 1):
        print(
            f"❌ FAILED: Expected at least {test_case['min_projects']} projects, got {total_projects}")
    else:
        print(f"✅ PASSED: Found {total_projects} projects")

        # Check websites if applicable
        if 'expected_websites' in test_case:
            websites = [g.get('website') for g in groups]
            expected = test_case['expected_websites']
            if all(w in websites for w in expected):
                print(f"   ✅ Websites: {set(websites)}")
            else:
                print(
                    f"❌ Website mismatch. Expected {expected}, got {set(websites)}")

        # Show sample projects
        sample_count = 0
        for group in groups[:2]:  # First 2 groups
            for proj in group.get('projects', [])[:2]:  # First 2 projects per group
                if sample_count == 0:
                    print(f"   Sample projects:")
                print(f"      - {proj.get('title', 'Unknown')[:70]}")
                sample_count += 1

print("\n" + "="*70)
print("ALL TESTS COMPLETED")
print("="*70)
