# ParseHub Data Ingestion - Complete Usage Guide

This guide shows you how to use the data ingestion system in different ways.

## Quick Start (5 minutes)

### 1. Start the Backend
```bash
cd backend
python api_server.py
```

Backend will start on `http://127.0.0.1:5000`

### 2. Ingest Data (Python)
```python
import requests

# Trigger data ingestion for a project
response = requests.post(
    "http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj",
    params={"days_back": 30}
)

print(response.json())
# Output:
# {
#   "success": true,
#   "ingestion_result": {
#     "completed_runs": 7,
#     "skipped_runs": 0,
#     "total_products_inserted": 10953
#   },
#   "statistics": { ... }
# }
```

### 3. Query Products (cURL)
```bash
# Get 10 products
curl "http://127.0.0.1:5000/api/products/43?limit=10&offset=0"

# Get 5 products with pretty formatting
curl "http://127.0.0.1:5000/api/products/43?limit=5" | jq .

# Get statistics
curl "http://127.0.0.1:5000/api/products/43/stats" | jq .

# Export to CSV
curl "http://127.0.0.1:5000/api/products/43/export" -o products.csv
```

---

## Usage Methods

### Method 1: One-Time Ingestion (Python)

Use this when you want to ingest data on-demand:

```python
import requests
import json

def ingest_project_data(project_token, days_back=30):
    """Ingest data for a project"""
    
    response = requests.post(
        "http://127.0.0.1:5000/api/ingest/{token}",
        params={"days_back": days_back}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   Completed runs: {result['ingestion_result']['completed_runs']}")
        print(f"   Products inserted: {result['ingestion_result']['total_products_inserted']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return False

# Example
ingest_project_data("teFu8XF3xYrj", days_back=30)
```

### Method 2: Scheduled Ingestion (Background Process)

Use the scheduler to automatically ingest data at regular intervals:

```bash
# Install scheduler
pip install schedule

# Run scheduler (will ingest every 6 hours)
python data_ingestion_scheduler.py

# Output:
# [2024-01-15 09:00:00] 🚀 Starting batch ingestion for 1 projects
# [2024-01-15 09:00:02] ✅ MANN FILTER Project: 7 runs, 10953 new products, 10953 total
# [2024-01-15 09:00:02] 📊 Batch Complete: 1 ✅, 0 ❌
```

To customize the scheduler, edit `data_ingestion_scheduler.py`:

```python
# Change project list
PROJECTS_TO_INGEST = [
    ("teFu8XF3xYrj", "MANN FILTER Project"),
    ("YOUR_TOKEN_2", "Another Project"),
]

# Change interval (in hours)
INGEST_INTERVAL_HOURS = 6

# Change lookback period (in days)
DAYS_LOOKBACK = 1
```

### Method 3: Manual Ingestion (cURL)

One-time data ingestion from command line:

```bash
# Ingest with 30-day lookback
curl -X POST "http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj?days_back=30"

# Ingest with 7-day lookback
curl -X POST "http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj?days_back=7"

# Ingest all runs (days_back=0)
curl -X POST "http://127.0.0.1:5000/api/ingest/teFu8XF3xYrj?days_back=0"
```

### Method 4: Batch Ingestion Script

Ingest multiple projects at once:

```python
import requests
import time

def batch_ingest(project_list):
    """Ingest multiple projects"""
    
    results = []
    
    for token, name in project_list:
        print(f"Ingesting {name}...")
        
        response = requests.post(
            f"http://127.0.0.1:5000/api/ingest/{token}",
            params={"days_back": 7}
        )
        
        if response.status_code == 200:
            result = response.json()['ingestion_result']
            results.append({
                'project': name,
                'products': result['total_products_inserted'],
                'status': '✅'
            })
        else:
            results.append({
                'project': name,
                'products': 0,
                'status': '❌'
            })
        
        time.sleep(2)  # Small delay between requests
    
    # Print summary
    print("\n" + "="*50)
    print("BATCH INGESTION SUMMARY")
    print("="*50)
    for r in results:
        print(f"{r['status']} {r['project']}: {r['products']} products")

# Example
projects = [
    ("teFu8XF3xYrj", "MANN FILTER"),
    ("project_token_2", "Project 2"),
    ("project_token_3", "Project 3"),
]

batch_ingest(projects)
```

---

## Querying Data

### Get Products with Pagination
```python
import requests

# Get 100 products starting at offset 0
response = requests.get(
    "http://127.0.0.1:5000/api/products/43",
    params={"limit": 100, "offset": 0}
)

products = response.json()['data']
total_count = response.json()['count']

for product in products:
    print(f"{product['name']} - {product['part_number']} - {product['sale_price']} {product['currency']}")

# Output:
# Filter für AdBlue® U 1003 - U 1003 (10) - 6.01 EURO
# Filter für AdBlue® U 1005 - U 1005 - 11.63 EURO
# ...
```

### Get Products by Run
```python
import requests

# Get products from specific run
response = requests.get(
    "http://127.0.0.1:5000/api/products/run/tnSTqK7a-w4T",
    params={"limit": 50}
)

products = response.json()['data']
print(f"Found {len(products)} products from this run")
```

### Get Statistics
```python
import requests

response = requests.get("http://127.0.0.1:5000/api/products/43/stats")
stats = response.json()['statistics']

print(f"Total products: {stats['total_products']}")
print(f"Latest extraction: {stats['latest_extraction']}")
print(f"Countries: {stats['top_countries']}")

# Output:
# Total products: 10953
# Latest extraction: February 19, 2026
# Countries: [{'country': 'Germany', 'count': 10953}]
```

### Export to CSV
```bash
# Download CSV file
curl "http://127.0.0.1:5000/api/products/43/export" -o products.csv

# Open in Excel/Sheets
# CSV will contain all products with columns:
# - name
# - part_number
# - brand
# - sale_price
# - country
# - extraction_date
# - ... and all other fields
```

---

## Python Helper Functions

Add these to your code for easier usage:

```python
import requests
from datetime import datetime

class ParseHubAPI:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
    
    def ingest(self, project_token, days_back=30):
        """Trigger data ingestion"""
        response = requests.post(
            f"{self.base_url}/api/ingest/{project_token}",
            params={"days_back": days_back}
        )
        return response.json() if response.status_code == 200 else None
    
    def get_products(self, project_id, limit=100, offset=0):
        """Get products from project"""
        response = requests.get(
            f"{self.base_url}/api/products/{project_id}",
            params={"limit": limit, "offset": offset}
        )
        return response.json() if response.status_code == 200 else None
    
    def get_products_by_run(self, run_token, limit=1000):
        """Get products from specific run"""
        response = requests.get(
            f"{self.base_url}/api/products/run/{run_token}",
            params={"limit": limit}
        )
        return response.json() if response.status_code == 200 else None
    
    def get_stats(self, project_id):
        """Get project statistics"""
        response = requests.get(
            f"{self.base_url}/api/products/{project_id}/stats"
        )
        return response.json() if response.status_code == 200 else None
    
    def export_csv(self, project_id, filename=None):
        """Export products to CSV"""
        if not filename:
            filename = f"products_{project_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        response = requests.get(f"{self.base_url}/api/products/{project_id}/export")
        
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        return None

# Usage
api = ParseHubAPI()

# Ingest
result = api.ingest("teFu8XF3xYrj", days_back=7)
print(f"Ingested: {result['ingestion_result']['total_products_inserted']} products")

# Get products
products = api.get_products(43, limit=10)
for p in products['data']:
    print(f"• {p['name']} ({p['part_number']})")

# Get stats
stats = api.get_stats(43)
print(f"Total: {stats['statistics']['total_products']}")

# Export CSV
csv_file = api.export_csv(43)
print(f"Saved to: {csv_file}")
```

---

## Monitoring & Troubleshooting

### Check Backend Status
```bash
# Test if backend is running
curl http://127.0.0.1:5000/health

# Should return: {"status": "ok"}
```

### View Ingestion Logs
```bash
# If using scheduler, check logs
tail -f ingestion_scheduler.log

# Or check backend console output
# Look for lines like:
# [2024-01-15 09:00:02] Ingesting run tnSTqK7a-w4T
# [2024-01-15 09:00:05] Extracted 2190 products
```

### Test Individual Components
```python
# Test data ingestion service directly
from backend.data_ingestion_service import ParseHubDataIngestor
from backend.database import Database

db = Database()
ingestor = ParseHubDataIngestor(db)

# Get run data
run_data = ingestor.get_run_data("tnSTqK7a-w4T")
print(f"Run status: {run_data['status']}")

# Get output data
output_data = ingestor.get_run_output_data("tnSTqK7a-w4T")
print(f"Found {len(output_data)} items in output")

# Test extraction
products = ingestor._extract_products_from_structure(output_data)
print(f"Extracted {len(products)} products")
```

### Common Issues

**Issue: "Connection refused" error**
```
❌ Error: HTTPConnectionError
Solution: Make sure backend is running:
    cd backend && python api_server.py
```

**Issue: "No data found after ingestion"**
```
❌ 0 products inserted
Possible causes:
1. RunData has no "output" field
2. Output structure is different than expected
3. All runs are older than days_back parameter

Solutions:
1. Check raw ParseHub API response:
   curl "https://api.parsehub.com/v2/runs/{token}/data?api_key=YOUR_KEY"
2. Lower days_back parameter: days_back=7 or days_back=0
3. Check backend logs for extraction errors
```

**Issue: "Service timeout"**
```
❌ Request timed out after 30 seconds
Solution: Use longer timeout or smaller limit:
    requests.post(..., timeout=600)  # 10 minutes
    params={"limit": 100}  # Smaller batch size
```

---

## Advanced Usage

### Filter Products by Field
```python
# Get all products and filter locally
api = ParseHubAPI()
response = api.get_products(43, limit=1000)

# Get only products with "MANN" in name
mann_products = [
    p for p in response['data'] 
    if 'MANN' in p.get('name', '')
]
print(f"Found {len(mann_products)} MANN products")

# Get only products under €50
affordable = [
    p for p in response['data']
    if float(p.get('sale_price', 0) or 0) < 50
]
print(f"Found {len(affordable)} products under €50")
```

### Bulk Update Tracking
```python
import json
from datetime import datetime

def track_ingestion(projects):
    """Track ingestion across multiple projects"""
    
    tracking = {
        'timestamp': datetime.now().isoformat(),
        'projects': []
    }
    
    for token, name in projects:
        result = api.ingest(token, days_back=1)
        
        tracking['projects'].append({
            'name': name,
            'token': token,
            'products_inserted': result['ingestion_result']['total_products_inserted'],
            'total_products': result['statistics']['total_products']
        })
    
    # Save tracking data
    with open('ingestion_tracking.json', 'w') as f:
        json.dump(tracking, f, indent=2)
    
    return tracking

# Usage
projects = [("token1", "Project 1"), ("token2", "Project 2")]
track_ingestion(projects)
```

---

## Summary

| Method | When to Use | Command |
|--------|-----------|---------|
| **One-Time (Python)** | Ad-hoc ingestion | `requests.post("/api/ingest/...")` |
| **Scheduler** | Regular updates (every 6 hours) | `python data_ingestion_scheduler.py` |
| **cURL** | Command-line testing | `curl -X POST "...ingest/..."` |
| **Batch Script** | Multiple projects at once | Custom Python script |
| **Direct API** | Integrate into other tools | Import `ParseHubAPI` class |

Choose the method that fits your workflow best!

---

*For complete API reference, see `DATA_INGESTION_SYSTEM.md`*
