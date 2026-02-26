#!/usr/bin/env python3
"""
Ingest data from ALL projects in the database
NO USER PROMPTS - Just runs and ingests everything
"""
from database import ParseHubDatabase as Database
import requests
import json
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))


BASE_URL = "http://127.0.0.1:5000"


def get_all_project_tokens():
    """Get all project tokens from database"""
    try:
        db = Database()
        conn = db._get_connection()
        cursor = conn.cursor()

        # Get all projects with their tokens
        cursor.execute("SELECT id, token, title FROM projects ORDER BY id")
        projects = cursor.fetchall()
        conn.close()

        result = []
        for proj_id, token, proj_title in projects:
            if token:  # Only include projects with tokens
                result.append((proj_id, token, proj_title))

        return result
    except Exception as e:
        print(f"❌ Error getting project tokens: {e}")
        return []


def ingest_project(project_id, project_token, project_title, days_back=30):
    """Ingest data for a single project"""
    try:
        print(f"  🔄 Ingesting: {project_title[:50]} (ID: {project_id})")

        response = requests.post(
            f"{BASE_URL}/api/ingest/{project_token}",
            params={"days_back": days_back},
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            ingestion = result.get('ingestion_result', {})

            completed_runs = ingestion.get('completed_runs', 0)
            total_inserted = ingestion.get('total_products_inserted', 0)

            status = "✅" if total_inserted > 0 else "⏭️ "
            print(
                f"     {status} {completed_runs} runs, {total_inserted:,} products")

            return {
                'success': True,
                'project_id': project_id,
                'project_title': project_title,
                'runs': completed_runs,
                'products': total_inserted
            }
        else:
            print(f"     ❌ HTTP {response.status_code}")
            return {
                'success': False,
                'project_id': project_id,
                'project_title': project_title,
                'error': f"HTTP {response.status_code}"
            }

    except Exception as e:
        print(f"     ❌ Error: {str(e)[:50]}")
        return {
            'success': False,
            'project_id': project_id,
            'project_title': project_title,
            'error': str(e)[:50]
        }


def main():
    """Main function to ingest all projects"""
    print("\n" + "="*80)
    print("🚀 MULTI-PROJECT DATA INGESTION - AUTO MODE")
    print("="*80)

    # Get all projects
    print("\n📋 Getting all projects from database...\n")
    projects = get_all_project_tokens()

    if not projects:
        print("❌ No projects found in database!")
        return

    print(f"Found {len(projects)} projects:")
    for proj_id, token, title in projects:
        print(f"  {proj_id:3d}. {title[:60]}")

    print("\n" + "-"*80)
    print(f"Starting ingestion for {len(projects)} projects...\n")

    # Check if backend is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Backend is running\n")
    except:
        print("❌ Backend API is not running!")
        print("   Start it with: cd backend && python api_server.py")
        return

    # Ingest all projects
    results = []
    total_runs = 0
    total_products = 0
    successful = 0
    failed = 0

    for i, (proj_id, token, title) in enumerate(projects, 1):
        print(f"[{i}/{len(projects)}]")
        result = ingest_project(proj_id, token, title, days_back=30)
        results.append(result)

        if result['success']:
            successful += 1
            total_runs += result.get('runs', 0)
            total_products += result.get('products', 0)
        else:
            failed += 1

    # Summary
    print("\n" + "="*80)
    print("📊 INGESTION SUMMARY")
    print("="*80)

    print(f"\n✅ Statistics:")
    print(f"   Projects processed: {successful} successful, {failed} failed")
    print(f"   Total runs ingested: {total_runs}")
    print(f"   Total products stored: {total_products:,}")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save results to file
    results_file = "ingestion_results.json"
    try:
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_projects': len(projects),
                'successful': successful,
                'failed': failed,
                'total_runs': total_runs,
                'total_products': total_products,
                'details': results
            }, f, indent=2, ensure_ascii=False)
        print(f"\n📝 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

    print("\n" + "="*80)
    print("✅ INGESTION COMPLETE!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
