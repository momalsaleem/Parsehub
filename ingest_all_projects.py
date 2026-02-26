#!/usr/bin/env python3
"""
Ingest data from ALL projects in the database
Automatically overwrites duplicate products with latest data
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
        conn = db.get_connection()
        cursor = conn.cursor()

        # Get all unique project tokens
        cursor.execute("SELECT DISTINCT id, title FROM projects ORDER BY id")
        projects = cursor.fetchall()
        conn.close()

        result = []
        for proj_id, proj_title in projects:
            # Get token from runs table (most recent run)
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT project_token FROM runs 
                WHERE project_id = ? 
                LIMIT 1
            """, (proj_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                token = row[0]
                result.append((proj_id, token, proj_title))

        return result
    except Exception as e:
        print(f"❌ Error getting project tokens: {e}")
        return []


def ingest_project(project_id, project_token, project_title, days_back=30):
    """Ingest data for a single project"""
    try:
        print(f"  🔄 Ingesting: {project_title} (ID: {project_id})")

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
            print(f"     ❌ HTTP {response.status_code}: {response.text[:100]}")
            return {
                'success': False,
                'project_id': project_id,
                'project_title': project_title,
                'error': f"HTTP {response.status_code}"
            }

    except Exception as e:
        print(f"     ❌ Error: {str(e)}")
        return {
            'success': False,
            'project_id': project_id,
            'project_title': project_title,
            'error': str(e)
        }


def main():
    """Main function to ingest all projects"""
    print("\n" + "="*80)
    print("🚀 MULTI-PROJECT DATA INGESTION")
    print("="*80)

    # Get all projects
    print("\n📋 Getting all projects from database...\n")
    projects = get_all_project_tokens()

    if not projects:
        print("❌ No projects found in database!")
        return

    print(f"Found {len(projects)} projects:\n")

    # Show projects
    for proj_id, token, title in projects:
        print(f"  {proj_id:3d}. {title[:60]}")

    print("\n" + "-"*80)

    # Ask user for confirmation
    response = input(
        f"\n⚠️  Ingest data for all {len(projects)} projects? (yes/no): ").strip().lower()

    if response not in ['yes', 'y']:
        print("❌ Cancelled")
        return

    print()

    # Check if backend is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except:
        print("❌ Backend API is not running!")
        print("   Start it with: cd backend && python api_server.py")
        return

    print("✅ Backend is running\n")

    # Ingest all projects
    results = []
    total_runs = 0
    total_products = 0
    successful = 0
    failed = 0

    for proj_id, token, title in projects:
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

    print(f"\nProjects processed: {successful} ✅, {failed} ❌")
    print(f"Total runs ingested: {total_runs}")
    print(f"Total products stored: {total_products:,}")
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Detailed results
    print("\n" + "-"*80)
    print("DETAILED RESULTS:")
    print("-"*80)

    for result in results:
        if result['success']:
            print(f"✅ {result['project_title'][:50]:50s} | "
                  f"{result['products']:6,} products | {result['runs']} runs")
        else:
            print(f"❌ {result['project_title'][:50]:50s} | "
                  f"Error: {result['error']}")

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
