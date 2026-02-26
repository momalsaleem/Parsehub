#!/usr/bin/env python3
"""Test the run button functionality"""
import requests
import json

BASE_URL = "http://localhost:3000"  # Frontend
BACKEND_URL = "http://localhost:5000"  # Backend

print("\n" + "="*70)
print("TESTING RUN BUTTON FUNCTIONALITY")
print("="*70)

# Step 1: Get projects
print("\n1. Fetching projects...")
response = requests.get(
    f"{BASE_URL}/api/projects?page=1&limit=10"
)

if response.status_code != 200:
    print(f"❌ FAILED: Could not fetch projects: {response.status_code}")
    print(response.text)
    exit(1)

data = response.json()
projects = data.get('projects', [])

if not projects:
    print("❌ No projects found")
    exit(1)

project = projects[0]
token = project.get('token')
print(f"✅ Found {len(projects)} projects")
print(f"   Using project: {project.get('title', 'Unknown')}")
print(f"   Token: {token}")

# Step 2: Test the run endpoint
print(f"\n2. Testing /api/projects/run with project_token...")
run_response = requests.post(
    f"{BASE_URL}/api/projects/run",
    json={
        "project_token": token,
        "pages": 1
    },
    headers={
        "Content-Type": "application/json"
    }
)

print(f"   Status: {run_response.status_code}")
print(f"   Response: {run_response.text[:200]}")

if run_response.status_code == 200:
    run_data = run_response.json()
    if run_data.get('success'):
        print(f"\n✅ RUN BUTTON WORKS!")
        print(f"   ✅ Run token: {run_data.get('run_token')}")
        print(f"   ✅ Status: {run_data.get('status')}")
        print(f"   ✅ Pages: {run_data.get('pages')}")
    else:
        print(f"\n❌ Run failed: {run_data.get('error')}")
else:
    print(f"\n❌ Run endpoint error: {run_response.status_code}")
    print(f"   {run_response.text}")

# Step 3: Also test with 'token' field (for backwards compatibility)
print(f"\n3. Testing /api/projects/run with token field...")
run_response2 = requests.post(
    f"{BASE_URL}/api/projects/run",
    json={
        "token": token,
        "pages": 1
    },
    headers={
        "Content-Type": "application/json"
    }
)

print(f"   Status: {run_response2.status_code}")

if run_response2.status_code == 200:
    run_data2 = run_response2.json()
    if run_data2.get('success'):
        print(f"✅ Token field also works!")
    else:
        print(f"⚠️  Token field failed: {run_data2.get('error')}")
else:
    print(f"⚠️  Token field error: {run_response2.status_code}")

print("\n" + "="*70)
