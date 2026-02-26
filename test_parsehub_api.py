#!/usr/bin/env python3
"""
Test ParseHub API directly to verify API key and project running.
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load env vars
load_dotenv('backend/.env')

API_KEY = os.getenv('PARSEHUB_API_KEY')
print(
    f"[TEST] Using API Key: {API_KEY[:10]}..." if API_KEY else "[TEST] ❌ No API Key found")

if not API_KEY:
    print("❌ CRITICAL: PARSEHUB_API_KEY not found in .env file")
    exit(1)

BASE_URL = "https://www.parsehub.com/api/v2"

print("\n" + "="*60)
print("TEST 1: Verify API Key by fetching account info")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/account",
                            params={"api_key": API_KEY}, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        print("✅ API Key is valid!")
    else:
        print("❌ API Key may be invalid or expired")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("TEST 2: Fetch all projects to find a runnable one")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/projects",
                            params={"api_key": API_KEY}, timeout=10)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        projects = response.json().get('projects', [])
        print(f"✅ Found {len(projects)} projects")

        if projects:
            first_project = projects[0]
            print(f"\nFirst project:")
            print(f"  Token: {first_project.get('token')}")
            print(f"  Title: {first_project.get('title')}")
            print(f"  Status: {first_project.get('status')}")
            print(f"  Last Run: {first_project.get('last_run')}")

            PROJECT_TOKEN = first_project.get('token')

            print("\n" + "="*60)
            print(f"TEST 3: Get details of project {PROJECT_TOKEN}")
            print("="*60)

            response = requests.get(
                f"{BASE_URL}/projects/{PROJECT_TOKEN}",
                params={"api_key": API_KEY},
                timeout=10
            )
            print(f"Status Code: {response.status_code}")
            project_details = response.json()
            print(f"Project Details: {json.dumps(project_details, indent=2)}")

            print("\n" + "="*60)
            print(f"TEST 4: RUN project {PROJECT_TOKEN}")
            print("="*60)

            run_data = {
                'api_key': API_KEY,
                'pages': 1
            }

            response = requests.post(
                f"{BASE_URL}/projects/{PROJECT_TOKEN}/run",
                data=run_data,
                timeout=10
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")

            if response.status_code == 200:
                run_info = response.json()
                if run_info.get('status') == 'running':
                    print("✅ Project is ACTUALLY RUNNING on ParseHub!")
                elif run_info.get('status') == 'initialized':
                    print(
                        "⚠️ Project initialized but not running yet (may start shortly)")

                    RUN_TOKEN = run_info.get('run_token')
                    if RUN_TOKEN:
                        print(f"\nWaiting 3 seconds then checking run status...")
                        import time
                        time.sleep(3)

                        response = requests.get(
                            f"{BASE_URL}/runs/{RUN_TOKEN}",
                            params={"api_key": API_KEY},
                            timeout=10
                        )
                        print(
                            f"Run Status Check - Code: {response.status_code}")
                        print(
                            f"Run Status: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"❌ Failed to start project: {response.json()}")
    else:
        print(f"❌ Failed to fetch projects: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("TEST 5: Check the specific project we've been testing")
print("="*60)

TEST_PROJECT = "teFu8XF3xYrj"
print(f"Testing project: {TEST_PROJECT}")

try:
    # Get project details
    response = requests.get(
        f"{BASE_URL}/projects/{TEST_PROJECT}",
        params={"api_key": API_KEY},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        project = response.json()
        print(f"Project Status: {project.get('status')}")
        print(f"Project Title: {project.get('title')}")
        print(f"Last Run: {project.get('last_run')}")

        # Try to run it
        print(f"\nAttempting to run {TEST_PROJECT}...")
        run_data = {
            'api_key': API_KEY,
            'pages': 1
        }

        response = requests.post(
            f"{BASE_URL}/projects/{TEST_PROJECT}/run",
            data=run_data,
            timeout=10
        )
        print(f"Run Response Status: {response.status_code}")
        run_info = response.json()
        print(f"Run Response: {json.dumps(run_info, indent=2)}")

        if response.status_code == 200:
            status = run_info.get('status')
            run_token = run_info.get('run_token')
            print(f"\n✅ Run started!")
            print(f"   Status: {status}")
            print(f"   Run Token: {run_token}")

            if run_token:
                print(f"\nChecking run progress...")
                import time
                time.sleep(2)

                response = requests.get(
                    f"{BASE_URL}/runs/{run_token}",
                    params={"api_key": API_KEY},
                    timeout=10
                )
                run_status = response.json()
                print(f"Run Progress: {json.dumps(run_status, indent=2)}")
    else:
        print(f"❌ Project not found or error: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("""
If all tests pass:
  ✅ API key is valid
  ✅ Projects can be fetched
  ✅ Projects can be run
  
If a test fails:
  ❌ Check the error message above
  ❌ Verify API key is correct in .env file
  ❌ Check project tokens are valid
  ❌ Ensure projects are not locked/archived
""")
