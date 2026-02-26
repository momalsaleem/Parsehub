#!/usr/bin/env python3
"""Debug filtering - detailed response inspection"""
import requests
import json

BASE_URL = "http://localhost:5000"

# Test website filtering with detailed output
print("\nDEBUG: Fetching filtered results for website='Filter-technik.de'...")
response = requests.get(
    f"{BASE_URL}/api/projects/search",
    params={"website": "Filter-technik.de", "limit": 1000}
)

print(f"Status: {response.status_code}")
print(f"\nFull Response JSON:")
print(json.dumps(response.json(), indent=2))

# Also check /api/projects endpoint with website filter
print("\n\n=== ALSO CHECK /api/projects with website filter ===")
response2 = requests.get(
    f"{BASE_URL}/api/projects",
    params={"website": "Filter-technik.de", "limit": 50}
)
print(f"Status: {response2.status_code}")
print(f"\nFull Response JSON:")
print(json.dumps(response2.json(), indent=2))
