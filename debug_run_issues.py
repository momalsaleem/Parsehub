#!/usr/bin/env python3
"""Debug run project issues"""
import requests
import json
import os

print("\n" + "="*70)
print("DEBUGGING RUN PROJECT ISSUES")
print("="*70)

# Check environment
print("\n1. Checking environment...")
api_key = os.getenv('PARSEHUB_API_KEY')
print(f"   PARSEHUB_API_KEY: {'SET' if api_key else 'NOT SET'}")
if api_key:
    print(f"   Key preview: {api_key[:10]}...")

# Step 1: Get a project from the backend directly
print("\n2. Getting project from backend directly...")
response = requests.get("http://localhost:5000/api/projects?limit=5")
if response.status_code == 200:
    data = response.json()
    projects = data.get('projects', [])
    if projects:
        project = projects[0]
        token = project.get('token')
        print(f"   ✅ Got project: {project.get('title', 'Unknown')}")
        print(f"   Token: {token}")
    else:
        print("   ❌ No projects returned")
        exit(1)
else:
    print(f"   ❌ Failed: {response.status_code}")
    exit(1)

# Step 2: Test backend run endpoint directly
print(f"\n3. Testing backend /api/projects/{token}/run endpoint directly...")
run_response = requests.post(
    f"http://localhost:5000/api/projects/{token}/run",
    json={"pages": 1},
    timeout=10
)

print(f"   Status: {run_response.status_code}")
print(f"   Response text: {run_response.text[:300]}")

if run_response.status_code == 200:
    run_data = run_response.json()
    print(f"   ✅ Backend endpoint works!")
    print(f"      Run token: {run_data.get('run_token')}")
    print(f"      Status: {run_data.get('status')}")
else:
    print(f"   ❌ Backend run failed")
    try:
        error = run_response.json()
        print(f"      Error: {error}")
    except:
        print(f"      Response: {run_response.text}")

# Step 3: Test frontend run endpoint
print(f"\n4. Testing frontend /api/projects/run endpoint...")
frontend_response = requests.post(
    f"http://localhost:3000/api/projects/run",
    json={"project_token": token, "pages": 1},
    timeout=10
)

print(f"   Status: {frontend_response.status_code}")
print(f"   Response text: {frontend_response.text[:300]}")

if frontend_response.status_code == 200:
    resp_data = frontend_response.json()
    if resp_data.get('success'):
        print(f"   ✅ Frontend endpoint works!")
        print(f"      Run token: {resp_data.get('run_token')}")
    else:
        print(f"   ❌ Frontend run failed: {resp_data.get('error')}")
else:
    print(f"   ❌ Frontend endpoint error: {frontend_response.status_code}")

# Step 4: Check if project is already running
print(f"\n5. Checking project status...")
status_response = requests.get(
    f"http://localhost:5000/api/projects/{token}"
)

if status_response.status_code == 200:
    proj_data = status_response.json()
    data = proj_data.get('data', {})
    last_run = data.get('last_run')
    if last_run:
        status = last_run.get('status')
        print(f"   Last run status: {status}")
        if status == 'running':
            print(f"   ⚠️  Project is already running!")
    else:
        print(f"   ✅ Project is not running")
else:
    print(f"   Could not get status")

print("\n" + "="*70)
