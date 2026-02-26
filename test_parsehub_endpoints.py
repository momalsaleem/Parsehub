#!/usr/bin/env python3
"""
Test various ParseHub API endpoints to find raw data
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

API_KEY = os.getenv('PARSEHUB_API_KEY')
RUN_TOKEN = "tnSTqK7a-w4T"  # Use a known complete run token

print("="*60)
print("TESTING PARSEHUB API ENDPOINTS")
print("="*60)

endpoints_to_test = [
    (f"https://www.parsehub.com/api/v2/runs/{RUN_TOKEN}",
     {'api_key': API_KEY}),
    (f"https://www.parsehub.com/api/v2/runs/{RUN_TOKEN}/output", {
     'api_key': API_KEY}),
    (f"https://www.parsehub.com/api/v2/runs/{RUN_TOKEN}/data",
     {'api_key': API_KEY}),
    (f"https://www.parsehub.com/api/v2/runs/{RUN_TOKEN}.json",
     {'api_key': API_KEY}),
]

for endpoint, params in endpoints_to_test:
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"{'='*60}")
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(
                f"Response keys: {list(data.keys()) if isinstance(data, dict) else f'List with {len(data)} items'}")

            # Show sample
            if isinstance(data, dict) and 'data' in data:
                sample = data['data']
                if isinstance(sample, list) and sample:
                    print(f"Found data list with {len(sample)} items")
                    print(
                        f"First item: {json.dumps(sample[0], indent=2, default=str)[:300]}")
            elif isinstance(data, list) and data:
                print(f"Got list with {len(data)} items")
                print(
                    f"First item: {json.dumps(data[0], indent=2, default=str)[:300]}")
            elif isinstance(data, dict):
                print(
                    f"Response (first 500 chars): {json.dumps(data, indent=2, default=str)[:500]}")
        else:
            print(f"Status {response.status_code}: {response.text[:200]}")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "="*60)
print("CHECKING PROJECT FOR DATA ACCESS")
print("="*60)

PROJECT_TOKEN = "teFu8XF3xYrj"

try:
    # Check if we can get data via the job/task endpoint
    response = requests.get(
        f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}",
        params={'api_key': API_KEY},
        timeout=10
    )

    if response.status_code == 200:
        project = response.json()

        # Check last_ready_run
        if 'last_ready_run' in project:
            last_run = project['last_ready_run']
            print(f"\nFound last_ready_run:")
            print(f"  Run token: {last_run.get('run_token')}")
            print(f"  Status: {last_run.get('status')}")
            print(f"  Data ready: {last_run.get('data_ready')}")

            # Try to fetch this run's data
            run_token = last_run.get('run_token')
            if run_token:
                print(f"\nTrying to fetch data for run: {run_token}")

                # Try CSV export
                csv_response = requests.get(
                    f"https://www.parsehub.com/api/v2/runs/{run_token}",
                    params={'api_key': API_KEY},
                    timeout=10
                )

                print(f"Run info status: {csv_response.status_code}")
                run_info = csv_response.json()
                print(f"Run info keys: {list(run_info.keys())}")

                # Check for data in run
                if 'data' in run_info:
                    print(f"✅ Found 'data' key!")
                    print(f"Data type: {type(run_info['data'])}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("""
ParseHub API notes:
- The /runs/{run_token} endpoint returns run metadata, NOT the data
- To get actual scraped data, you may need to:
  1. Access via webhook if configured
  2. Set output_type to csv and parse as CSV
  3. Use a different endpoint not documented here
  4. Check if data is limited to paid plans

Your runs show data_ready=1, which suggests data exists
but the standard API may not expose it for free plans.
""")
