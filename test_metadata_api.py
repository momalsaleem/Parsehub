import requests
import json

response = requests.get(
    'http://localhost:5000/api/metadata?project_token=tsTA0g3nsdNd',
    headers={'Authorization': 'Bearer t_hmXetfMCq3'}
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
