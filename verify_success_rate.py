import requests
import json

response = requests.get(
    'http://localhost:5000/api/projects/tsTA0g3nsdNd',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'}
)

print(f"Status Code: {response.status_code}")
data = response.json()

if 'run_stats' in data:
    print(f"\nRun Stats:")
    print(f"  Total Runs: {data['run_stats']['total_runs']}")
    print(f"  Completed Runs: {data['run_stats']['completed_runs']}")
    print(f"  Pages Scraped: {data['run_stats']['pages_scraped']}")
    print(f"  Success Rate: {data['run_stats']['success_rate']}%")
else:
    print("No run_stats in response")
    print(json.dumps(data, indent=2, default=str))
