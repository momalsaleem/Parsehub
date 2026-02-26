import requests

print("Triggering Auto-Sync to populate database...")
print("="*60)

# Trigger manual sync
response = requests.post(
    "http://localhost:5000/api/sync/trigger",
    headers={"Authorization": "Bearer t_hmXetfMCq3"}
)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Sync completed!")
    print(f"\nResults:")
    results = data.get('results', {})
    print(f"  Projects synced: {results.get('projects_synced', 0)}")
    print(f"  Projects updated: {results.get('projects_updated', 0)}")
    print(f"  Runs updated: {results.get('runs_updated', 0)}")
else:
    print(f"\n❌ Sync failed: {response.text}")

print("\n" + "="*60)
