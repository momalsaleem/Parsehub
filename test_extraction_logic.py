#!/usr/bin/env python3
"""
Test the product extraction logic directly
"""
from data_ingestion_service import ParseHubDataIngestor
import sys
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv('backend/.env')

# Import the ingestion service
sys.path.insert(0, 'backend')

RUN_TOKEN = "tnSTqK7a-w4T"

print("="*60)
print("TESTING PRODUCT EXTRACTION")
print("="*60)

ingestor = ParseHubDataIngestor()

print(f"\nFetching raw data from run: {RUN_TOKEN}")
raw_data = ingestor.get_run_output_data(RUN_TOKEN)

print(f"Raw data type: {type(raw_data)}")
if raw_data:
    if isinstance(raw_data, dict):
        print(f"Raw data keys: {list(raw_data.keys())}")
        print(
            f"Sample (first 500 chars):\n{json.dumps(raw_data, indent=2, default=str)[:500]}")
    elif isinstance(raw_data, list):
        print(f"Raw data list length: {len(raw_data)}")
        if raw_data:
            print(
                f"First item: {json.dumps(raw_data[0], indent=2, default=str)[:300]}")
else:
    print("❌ No raw data returned")

print("\n" + "="*60)
print("TESTING PARSING")
print("="*60)

# Fetch from API and parse
API_KEY = os.getenv('PARSEHUB_API_KEY')
BASE_URL = 'https://www.parsehub.com/api/v2'

response = requests.get(
    f'{BASE_URL}/runs/{RUN_TOKEN}/data',
    params={'api_key': API_KEY},
    timeout=30
)

api_data = response.json()
print(f"\nAPI Response type: {type(api_data)}")
print(
    f"API Response keys: {list(api_data.keys()) if isinstance(api_data, dict) else 'List'}")

# Test extraction
extracted = ingestor._extract_products_from_structure(api_data)
print(f"\n✅ Extracted {len(extracted)} products")

if extracted:
    print(f"\nFirst extracted product:")
    print(json.dumps(extracted[0], indent=2, default=str))

    print(f"\nFirst 5 products summary:")
    for i, product in enumerate(extracted[:5]):
        print(
            f"{i+1}. {product.get('name', 'N/A')} - {product.get('part_number', 'N/A')}")
else:
    print("❌ No products extracted")
    print("\nFull API data:")
    print(json.dumps(api_data, indent=2, default=str)[:1000])
