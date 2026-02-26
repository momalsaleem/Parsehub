import requests
import json

# Test the updated project endpoint
print("Testing Updated Project Endpoint...")
print("="*60)

# Sample project token from the screenshot
token = "tq3KfpOZe-d6"  # (MSA Project) chareonmarinestore.com_ParkerRacor

print(f"\n1. Testing GET /api/projects/{token}")
print("-"*60)

try:
    response = requests.get(
        f"http://localhost:5000/api/projects/{token}",
        headers={"Authorization": "Bearer t_hmXetfMCq3"}
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        if data.get('success'):
            project_data = data.get('data', {})

            print("\n✅ Project found!")
            print(f"\nProject Details:")
            print(f"  ID: {project_data.get('id')}")
            print(f"  Title: {project_data.get('title')}")
            print(f"  Token: {project_data.get('token')}")
            print(f"  Owner: {project_data.get('owner_email')}")
            print(f"  Main Site: {project_data.get('main_site')}")
            print(f"  Created: {project_data.get('created_at')}")
            print(f"  Updated: {project_data.get('updated_at')}")

            # Last Run Info
            last_run = project_data.get('last_run')
            if last_run:
                print(f"\n📊 Last Run:")
                print(f"  Run Token: {last_run.get('run_token')}")
                print(f"  Status: {last_run.get('status')}")
                print(f"  Pages Scraped: {last_run.get('pages', 0)}")
                print(f"  Start Time: {last_run.get('start_time')}")
                print(f"  End Time: {last_run.get('end_time')}")
            else:
                print(f"\n📊 Last Run: None")

            # Run Statistics
            run_stats = project_data.get('run_stats')
            if run_stats:
                print(f"\n📈 Run Statistics:")
                print(f"  Total Runs: {run_stats.get('total_runs', 0)}")
                print(
                    f"  Completed Runs: {run_stats.get('completed_runs', 0)}")
                print(f"  Active Runs: {run_stats.get('active_runs', 0)}")
                print(
                    f"  Pages Scraped (Total): {run_stats.get('pages_scraped', 0)}")
                print(f"  Success Rate: {run_stats.get('success_rate', 0)}%")
                print(
                    f"  Avg Pages/Run: {run_stats.get('average_pages_per_run', 0)}")
            else:
                print(f"\n📈 Run Statistics: None")

            # Metadata
            metadata = project_data.get('metadata', [])
            if metadata:
                print(f"\n📋 Metadata: {len(metadata)} record(s)")
                for i, meta in enumerate(metadata[:3]):  # Show first 3
                    print(f"  {i+1}. {meta.get('project_name', 'N/A')}")
                    if meta.get('total_products'):
                        print(f"     Products: {meta.get('total_products')}")
                    if meta.get('total_pages'):
                        print(f"     Pages: {meta.get('total_pages')}")
        else:
            print(f"\n❌ Error: {data.get('error')}")
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test completed!")
