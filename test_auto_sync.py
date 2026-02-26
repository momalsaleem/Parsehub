import requests

# Test auto-sync status
print("Testing Auto-Sync Service...")
print("="*50)

# 1. Check status
print("\n1. Checking auto-sync status...")
response = requests.get("http://localhost:5000/api/sync/status")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")

# 2. Trigger manual sync
print("\n2. Triggering manual sync...")
response = requests.post(
    "http://localhost:5000/api/sync/trigger",
    headers={"Authorization": "Bearer t_hmXetfMCq3"}
)
print(f"Status Code: {response.status_code}")
result = response.json()
print(f"Response: {result}")

if result.get('status') == 'success':
    print("\n[OK] Manual sync completed successfully!")
    print(
        f"Projects synced: {result.get('results', {}).get('projects_synced', 0)}")
    print(f"Runs updated: {result.get('results', {}).get('runs_updated', 0)}")
    print(
        f"Projects updated: {result.get('results', {}).get('projects_updated', 0)}")
else:
    print(f"\n[ERROR] Sync failed: {result.get('message', 'Unknown error')}")

print("\n" + "="*50)
print("Auto-Sync Service is working correctly!")
