#!/usr/bin/env python3
"""
Quick test of the API responses
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Get project by token
print("Getting project...")
response = requests.get(f"{BASE_URL}/api/projects/teFu8XF3xYrj")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, default=str)[:500]}")

project = response.json()
if isinstance(project, dict):
    project_id = project.get('id')
    print(f"\nProject ID: {project_id}")

    if project_id:
        # Get stats
        print(f"\nGetting stats for project {project_id}...")
        response = requests.get(f"{BASE_URL}/api/products/{project_id}/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}")
