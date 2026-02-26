#!/usr/bin/env python3
"""Detailed test of run endpoint"""
import requests
import json

# Get a project
response = requests.get("http://localhost:5000/api/projects?limit=1")
projects = response.json().get('projects', [])
if projects:
    token = projects[0].get('token')
    print(f"Testing with project: {token}")

    # Test the run endpoint
    print("\nCalling /api/projects/{token}/run...")
    run_response = requests.post(
        f"http://localhost:5000/api/projects/{token}/run",
        json={"pages": 1},
        timeout=10
    )

    print(f"Status Code: {run_response.status_code}")
    print(f"Headers: {dict(run_response.headers)}")
    print(f"Full Response: {json.dumps(run_response.json(), indent=2)}")

    # Check if there's an error in the response
    data = run_response.json()
    if 'error' in data:
        print(f"\n❌ ERROR: {data['error']}")
    elif data.get('success') == False:
        print(f"\n❌ FAILED: {data}")
    else:
        print(f"\n✅ SUCCESS: Run token = {data.get('run_token')}")
