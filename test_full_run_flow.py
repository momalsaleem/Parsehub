#!/usr/bin/env python3
"""
Test the complete run flow from frontend API to ParseHub
"""
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('PARSEHUB_API_KEY')
BACKEND_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://127.0.0.1:3000"

PROJECT_TOKEN = "teFu8XF3xYrj"

print("="*60)
print("STEP 1: Run project via backend API")
print("="*60)

try:
    response = requests.post(
        f"{BACKEND_URL}/api/projects/{PROJECT_TOKEN}/run",
        json={"pages": 1},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        backend_run_token = response.json().get('run_token')
        print(f"✅ Backend run started with token: {backend_run_token}")
    else:
        print(f"❌ Backend run failed")
        exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n" + "="*60)
print("STEP 2: Check project status on ParseHub")
print("="*60)

time.sleep(2)

try:
    response = requests.get(
        f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}",
        params={"api_key": API_KEY},
        timeout=10
    )

    if response.status_code == 200:
        project = response.json()
        print(f"Project Title: {project.get('title')}")
        print(
            f"Last Run Token: {project.get('last_run', {}).get('run_token')}")
        print(f"Last Run Status: {project.get('last_run', {}).get('status')}")

        last_run_token = project.get('last_run', {}).get('run_token')
        if last_run_token:
            print(f"✅ Project has active run: {last_run_token}")
except Exception as e:
    print(f"❌ Error checking project: {e}")

print("\n" + "="*60)
print("STEP 3: Check run status directly on ParseHub")
print("="*60)

if last_run_token:
    try:
        response = requests.get(
            f"https://www.parsehub.com/api/v2/runs/{last_run_token}",
            params={"api_key": API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            run = response.json()
            print(f"Run Token: {run.get('run_token')}")
            print(f"Status: {run.get('status')}")
            print(f"Pages: {run.get('pages')}")
            print(f"Data Ready: {run.get('data_ready')}")

            if run.get('status') == 'running':
                print(f"✅ Project IS RUNNING!")
                print(f"   Start Time: {run.get('start_running_time')}")
            elif run.get('status') == 'initialized':
                print(f"⏳ Project INITIALIZED (may start shortly)")
            elif run.get('status') == 'complete':
                print(f"✅ Run COMPLETED")
    except Exception as e:
        print(f"❌ Error checking run: {e}")

print("\n" + "="*60)
print("STEP 4: Fetch project details from frontend API")
print("="*60)

try:
    response = requests.get(
        f"{FRONTEND_URL}/api/projects/{PROJECT_TOKEN}",
        timeout=10
    )

    if response.status_code == 200:
        project_data = response.json()
        print(f"Project Title: {project_data.get('title')}")
        last_run = project_data.get('last_run')
        if last_run:
            print(f"Last Run Status: {last_run.get('status')}")
            print(f"Last Run Token: {last_run.get('run_token')}")
        print(f"✅ Frontend API working")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("""
✅ If all steps pass, the run system is working correctly
❌ If step 1 fails: Check backend/ParseHub API key
❌ If step 2 fails: Project may not exist or API key invalid
❌ If step 3 fails: Run token not found (project might not have started)
❌ If step 4 fails: Frontend API not responding
""")
