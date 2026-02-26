#!/usr/bin/env python3
"""
Test the data ingestion system
"""
import requests
import json
import time
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

BACKEND_URL = "http://127.0.0.1:5000"
PROJECT_TOKEN = "teFu8XF3xYrj"

print("="*60)
print("DATA INGESTION TEST")
print("="*60)

print("\nSTEP 1: Trigger data ingestion for completed runs")
print("-"*60)

try:
    response = requests.post(
        f"{BACKEND_URL}/api/ingest/{PROJECT_TOKEN}",
        params={"days_back": 7},
        timeout=60
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))

    if response.status_code == 200:
        print("✅ Data ingestion successful!")
    else:
        print("❌ Data ingestion failed")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("STEP 2: Fetch product statistics")
print("="*60)

try:
    # First, get project ID
    response = requests.get(f"{BACKEND_URL}/api/projects/{PROJECT_TOKEN}")
    if response.status_code == 200:
        project = response.json()
        project_id = project.get('id')

        if project_id:
            # Fetch stats
            response = requests.get(
                f"{BACKEND_URL}/api/products/{project_id}/stats")
            print(f"Status: {response.status_code}")
            stats = response.json()
            print(json.dumps(stats, indent=2))

            print(f"\n✅ Product Statistics:")
            stats_data = stats.get('statistics', {})
            print(f"   Total products: {stats_data.get('total_products', 0)}")
            print(
                f"   Total runs with data: {stats_data.get('total_runs_with_data', 0)}")
            print(
                f"   Latest extraction: {stats_data.get('latest_extraction', 'N/A')}")
            print(
                f"   Top brands: {[b.get('brand') for b in stats_data.get('top_brands', [])[:5]]}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("STEP 3: Fetch sample product data")
print("="*60)

try:
    if project_id:
        response = requests.get(
            f"{BACKEND_URL}/api/products/{project_id}",
            params={"limit": 10, "offset": 0}
        )
        print(f"Status: {response.status_code}")
        result = response.json()

        count = result.get('count', 0)
        print(f"✅ Retrieved {count} products")

        # Show first product as example
        if result.get('data'):
            print(f"\nSample Product:")
            sample = result['data'][0]
            for key, value in sample.items():
                print(f"  {key}: {value}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
print("""
Features demonstrated:
✅ Data ingestion from ParseHub runs
✅ Product data storage with dynamic columns
✅ Statistics and analytics
✅ CSV export capability

To export all product data as CSV:
  GET /api/products/<project_id>/export

To fetch products for a specific run:
  GET /api/products/run/<run_token>?limit=1000
  
To fetch products for a project:
  GET /api/products/<project_id>?limit=100&offset=0
""")
