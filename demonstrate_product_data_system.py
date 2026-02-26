#!/usr/bin/env python3
"""
Complete Data Ingestion System - API Reference & Examples
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"
PROJECT_TOKEN = "teFu8XF3xYrj"

print("="*80)
print("DATA INGESTION & PRODUCT MANAGEMENT - COMPLETE SYSTEM")
print("="*80)

# Get project ID
response = requests.get(f"{BASE_URL}/api/projects/{PROJECT_TOKEN}")
api_response = response.json()

# Handle both response formats
if 'data' in api_response and isinstance(api_response['data'], dict):
    project = api_response['data']
elif isinstance(api_response, dict) and 'id' in api_response:
    project = api_response
else:
    print("❌ Unable to fetch project")
    exit(1)

project_id = project.get('id')
project_title = project.get('title') or (project.get('metadata', [{}])[
    0].get('project_name') if project.get('metadata') else None)

print(f"\n✅ Project: {project_title}")
print(f"   ID: {project_id}")
print(f"   Token: {PROJECT_TOKEN}")

if not project_id:
    print("❌ Could not find project ID")
    exit(1)

# ============= STATISTICS =============
print(f"\n{'='*80}")
print("1. PRODUCT STATISTICS")
print(f"{'='*80}")

response = requests.get(f"{BASE_URL}/api/products/{project_id}/stats")
api_response = response.json()

if 'statistics' in api_response:
    stats = api_response['statistics']
else:
    print(f"Error response: {api_response}")
    exit(1)

print(f"\nOverall Statistics:")
print(f"  ✅ Total Products: {stats.get('total_products', 0):,}")
print(f"  ✅ Runs with Data: {stats.get('total_runs_with_data', 0)}")
print(f"  ✅ Latest Extraction: {stats.get('latest_extraction', 'N/A')}")

print(f"\nTop Countries:")
for country in stats.get('top_countries', []):
    print(f"  • {country['country']}: {country['count']:,} products")

print(f"\nTop Brands:")
for brand in stats.get('top_brands', [])[:10]:
    if brand.get('brand'):
        print(f"  • {brand['brand']}: {brand['count']:,} products")

# ============= SAMPLE PRODUCTS =============
print(f"\n{'='*80}")
print("2. SAMPLE PRODUCTS (First 5)")
print(f"{'='*80}\n")

response = requests.get(
    f"{BASE_URL}/api/products/{project_id}?limit=5&offset=0")
api_response = response.json()

# Handle response format
if 'data' in api_response and isinstance(api_response['data'], list):
    products = api_response['data']
else:
    print(f"Unexpected response format: {list(api_response.keys())}")
    products = []

for i, product in enumerate(products, 1):
    print(f"Product {i}:")
    print(f"  Name: {product.get('name', 'N/A')}")
    print(f"  Part Number: {product.get('part_number', 'N/A')}")
    print(
        f"  Sale Price: {product.get('sale_price', 'N/A')} {product.get('currency', '')}")
    print(f"  Country: {product.get('country', 'N/A')}")
    print(f"  Page: {product.get('page_number', 'N/A')}")
    print(f"  Run: {product.get('run_token', 'N/A')[:6]}...")
    print()

# ============= RUN SPECIFIC DATA =============
print(f"\n{'='*80}")
print("3. PRODUCTS BY RUN")
print(f"{'='*80}\n")

# Get a sample run token from products
run_token = products[0].get('run_token') if products else None

if run_token:
    response = requests.get(f"{BASE_URL}/api/products/run/{run_token}?limit=3")
    run_products = response.json()

    print(f"Run Token: {run_token}")
    print(f"Products in this run: {run_products.get('count', 0)}")
    print(f"\nSample products from this run:")

    for product in run_products.get('data', [])[:3]:
        print(
            f"  • {product.get('name', 'N/A')} ({product.get('part_number', 'N/A')})")

# ============= DATA STRUCTURE =============
print(f"\n{'='*80}")
print("4. DATABASE SCHEMA")
print(f"{'='*80}\n")

if products:
    print("Product Data Columns:")
    sample = products[0]
    for key in sorted(sample.keys()):
        value = sample[key]
        value_type = type(value).__name__
        print(f"  • {key}: {value_type}")

print(f"\n{'='*80}")
print("5. API ENDPOINTS AVAILABLE")
print(f"{'='*80}\n")

endpoints = [
    ("POST", "/api/ingest/<project_token>",
     "Trigger data ingestion from ParseHub runs", "days_back=30"),
    ("GET", "/api/products/<project_id>",
     "Fetch products for a project", "limit=100&offset=0"),
    ("GET", "/api/products/run/<run_token>",
     "Fetch products for a specific run", "limit=1000"),
    ("GET", "/api/products/<project_id>/stats", "Get product statistics", ""),
    ("GET", "/api/products/<project_id>/export", "Export products as CSV", ""),
]

for method, endpoint, description, params in endpoints:
    print(f"{method:4} {endpoint}")
    print(f"     {description}")
    if params:
        print(f"     Query: {params}")
    print()

print(f"\n{'='*80}")
print("USAGE EXAMPLES")
print(f"{'='*80}\n")

print("""
1. Ingest data from ParseHub runs:
   curl -X POST "http://127.0.0.1:5000/api/ingest/{project_token}?days_back=30"

2. Get all products for a project:
   curl "http://127.0.0.1:5000/api/products/{project_id}?limit=100&offset=0"

3. Get products from a specific run:
   curl "http://127.0.0.1:5000/api/products/run/{run_token}?limit=1000"

4. Get statistics:
   curl "http://127.0.0.1:5000/api/products/{project_id}/stats"

5. Export all products as CSV:
   curl "http://127.0.0.1:5000/api/products/{project_id}/export" -o products.csv

Python Examples:
-----------------

import requests

# Ingest data
response = requests.post(
    "http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj",
    params={"days_back": 30}
)
print(response.json())

# Get products
response = requests.get(
    "http://127.0.0.1:5000/api/products/1",
    params={"limit": 100, "offset": 0}
)
products = response.json()['data']

# Export
response = requests.get(
    "http://127.0.0.1:5000/api/products/1/export"
)
with open("products.csv", "wb") as f:
    f.write(response.content)
""")

print(f"\n{'='*80}")
print("✅ DATA INGESTION SYSTEM FULLY OPERATIONAL")
print(f"{'='*80}")
