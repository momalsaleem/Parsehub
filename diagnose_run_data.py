#!/usr/bin/env python3
"""
Diagnose ParseHub run data structure
"""
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

API_KEY = os.getenv('PARSEHUB_API_KEY')
PROJECT_TOKEN = "teFu8XF3xYrj"

print("="*60)
print("PARSEHUB RUN DATA STRUCTURE ANALYSIS")
print("="*60)

# Get project to find completed runs
try:
    response = requests.get(
        f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}",
        params={'api_key': API_KEY},
        timeout=30
    )
    project = response.json()

    run_list = project.get('run_list', [])

    # Find a complete run
    completed_runs = [r for r in run_list if r.get(
        'status') == 'complete' and r.get('data_ready')]

    if not completed_runs:
        print("❌ No completed runs with data found")
        exit(1)

    print(f"\n✅ Found {len(completed_runs)} completed runs")

    # Analyze the first completed run
    run = completed_runs[0]
    run_token = run.get('run_token')

    print(f"\nAnalyzing run: {run_token}")
    print(f"Status: {run.get('status')}")
    print(f"Data Ready: {run.get('data_ready')}")
    print(f"Pages: {run.get('pages')}")

    # Fetch run data
    print("\nFetching run data...")
    response = requests.get(
        f"https://www.parsehub.com/api/v2/runs/{run_token}",
        params={'api_key': API_KEY},
        timeout=30
    )

    run_data = response.json()

    print(f"\nRun Data Keys: {list(run_data.keys())}")

    # Check data structure
    if 'data' in run_data:
        data = run_data['data']
        print(f"\nData type: {type(data).__name__}")

        if isinstance(data, list):
            print(f"Data is a LIST with {len(data)} items")
            if data:
                print(f"First item type: {type(data[0]).__name__}")
                print(
                    f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'N/A'}")
                print(f"\nFirst item (sample):")
                print(json.dumps(data[0], indent=2, default=str)[:500])

        elif isinstance(data, dict):
            print(f"Data is a DICT with keys: {list(data.keys())}")

            # Check common nested structures
            for key in ['items', 'results', 'records', 'products', 'entries']:
                if key in data:
                    items = data[key]
                    print(f"\nFound nested '{key}': {type(items).__name__}")
                    if isinstance(items, list) and items:
                        print(f"  Contains {len(items)} items")
                        print(
                            f"  First item keys: {list(items[0].keys()) if isinstance(items[0], dict) else 'N/A'}")
                        print(f"  First item (sample):")
                        print(
                            f"  {json.dumps(items[0], indent=4, default=str)[:500]}")
                    break

    # Show full structure (truncated)
    print(f"\n\nFull Run Data Structure (first 1000 chars):")
    print(json.dumps(run_data, indent=2, default=str)[:1000])

    # List all keys at root level
    print(f"\n\nRoot level keys in run data:")
    for key in run_data.keys():
        value = run_data[key]
        if isinstance(value, (list, dict)):
            print(f"  {key}: {type(value).__name__} ({len(value)} items)")
        else:
            print(f"  {key}: {type(value).__name__}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
print("""
Use the structure found above to update the parse_run_data() function
in data_ingestion_service.py to correctly extract product data.
""")
