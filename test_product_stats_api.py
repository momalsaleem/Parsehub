#!/usr/bin/env python3
"""
Test that product stats are accessible via API
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test getting stats for project ID 43 (MANN FILTER)
print("="*80)
print("📊 API TEST: Product Statistics Endpoint")
print("="*80)

print("\n1. Testing: GET /api/products/43/stats (Project ID 43 - MANN FILTER)")
print("-" * 80)

try:
    response = requests.get(f"{BASE_URL}/api/products/43/stats", timeout=10)

    if response.status_code == 200:
        stats = response.json()
        print("✅ API Response Successful")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    else:
        print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test a few more projects
print("\n2. Testing: Multiple Projects")
print("-" * 80)

test_projects = [1, 2, 3, 43, 90]

for proj_id in test_projects:
    try:
        response = requests.get(
            f"{BASE_URL}/api/products/{proj_id}/stats", timeout=10)

        if response.status_code == 200:
            stats = response.json().get('statistics', {})
            total = stats.get('total_products', 0)
            runs = stats.get('total_runs_with_data', 0)

            if total > 0:
                print(
                    f"✅ Project {proj_id:3d}: {total:8,d} products, {runs} runs")
            else:
                print(f"⏭️  Project {proj_id:3d}: No data (0 products)")
        else:
            print(f"❌ Project {proj_id:3d}: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Project {proj_id:3d}: Error - {str(e)[:50]}")

print("\n" + "="*80)
print("✅ API TEST COMPLETE")
print("="*80 + "\n")
