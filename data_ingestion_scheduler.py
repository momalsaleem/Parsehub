#!/usr/bin/env python3
"""
ParseHub Continuous Data Ingestion Scheduler
Automatically fetches and stores ParseHub data at regular intervals
"""
import requests
import schedule
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

BASE_URL = "http://127.0.0.1:5000"

# Projects to ingest (add more project tokens as needed)
PROJECTS_TO_INGEST = [
    ("teFu8XF3xYrj", "MANN FILTER Project"),
    # Add more projects:
    # ("PROJECT_TOKEN_2", "Project Name 2"),
    # ("PROJECT_TOKEN_3", "Project Name 3"),
]

# Configuration
INGEST_INTERVAL_HOURS = 6  # Run ingestion every 6 hours
DAYS_LOOKBACK = 1  # Look back 1 day for new runs
LOG_FILE = "ingestion_scheduler.log"


def log_message(message: str):
    """Print and log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {message}"
    print(formatted)

    # Also write to log file
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except:
        pass


def ingest_single_project(project_token: str, project_name: str):
    """Ingest data for a single project"""
    try:
        log_message(f"🔄 Ingesting data for: {project_name}")

        # Trigger ingestion
        response = requests.post(
            f"{BASE_URL}/api/ingest/{project_token}",
            params={"days_back": DAYS_LOOKBACK},
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()

            ingestion = result.get('ingestion_result', {})
            stats = result.get('statistics', {})

            completed_runs = ingestion.get('completed_runs', 0)
            total_inserted = ingestion.get('total_products_inserted', 0)
            total_products = stats.get('total_products', 0)

            log_message(
                f"✅ {project_name}: "
                f"{completed_runs} runs, "
                f"{total_inserted} new products, "
                f"{total_products} total"
            )

            return True
        else:
            log_message(
                f"❌ {project_name}: HTTP {response.status_code} - {response.text[:100]}"
            )
            return False

    except Exception as e:
        log_message(f"❌ {project_name}: Error - {str(e)}")
        return False


def ingest_all_projects():
    """Ingest data for all configured projects"""
    log_message("="*70)
    log_message(
        f"🚀 Starting batch ingestion for {len(PROJECTS_TO_INGEST)} projects")
    log_message("="*70)

    success_count = 0
    fail_count = 0

    for project_token, project_name in PROJECTS_TO_INGEST:
        if ingest_single_project(project_token, project_name):
            success_count += 1
        else:
            fail_count += 1

        # Small delay between projects to avoid overloading
        time.sleep(2)

    log_message(f"\n📊 Batch Complete: {success_count} ✅, {fail_count} ❌")
    log_message("="*70 + "\n")


def get_project_statistics(project_token: str):
    """Get and display statistics for a project"""
    try:
        # Get project ID
        response = requests.get(f"{BASE_URL}/api/projects/{project_token}")

        if response.status_code == 200:
            api_response = response.json()

            # Handle response format
            if 'data' in api_response and isinstance(api_response['data'], dict):
                project = api_response['data']
            else:
                project = api_response

            project_id = project.get('id')

            if project_id:
                # Get stats
                response = requests.get(
                    f"{BASE_URL}/api/products/{project_id}/stats")

                if response.status_code == 200:
                    stats = response.json().get('statistics', {})
                    return {
                        'project_id': project_id,
                        'total_products': stats.get('total_products', 0),
                        'runs': stats.get('total_runs_with_data', 0),
                        'latest': stats.get('latest_extraction', 'N/A'),
                        'countries': [c['country'] for c in stats.get('top_countries', [])]
                    }
    except:
        pass

    return None


def schedule_jobs():
    """Schedule ingestion jobs"""
    # Schedule batch ingestion
    schedule.every(INGEST_INTERVAL_HOURS).hours.do(ingest_all_projects)

    # Also show daily statistics at a specific time
    schedule.every().day.at("09:00").do(
        lambda: log_message("Daily ingestion scheduled for today"))

    log_message(f"📅 Ingestion scheduled every {INGEST_INTERVAL_HOURS} hours")
    log_message(f"📅 Looking back {DAYS_LOOKBACK} day(s) for new runs")


def main():
    """Main scheduler loop"""
    log_message("\n" + "="*70)
    log_message("🎯 ParseHub Continuous Data Ingestion Scheduler")
    log_message("="*70)

    # Print configuration
    log_message(f"\n📋 Configuration:")
    log_message(f"   Projects: {len(PROJECTS_TO_INGEST)}")
    for token, name in PROJECTS_TO_INGEST:
        log_message(f"     • {name} ({token[:10]}...)")
    log_message(f"   Interval: Every {INGEST_INTERVAL_HOURS} hours")
    log_message(f"   Lookback: {DAYS_LOOKBACK} day(s)")
    log_message(f"   Backend URL: {BASE_URL}")
    log_message(f"   Log file: {LOG_FILE}\n")

    # Schedule jobs
    schedule_jobs()

    # Run initial ingestion
    log_message("Running initial ingestion...\n")
    ingest_all_projects()

    # Main loop
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check schedule every minute

    except KeyboardInterrupt:
        log_message("\n⛔ Scheduler stopped by user")
    except Exception as e:
        log_message(f"\n❌ Scheduler error: {e}")


if __name__ == "__main__":
    # Check if scheduler package is available
    try:
        import schedule
    except ImportError:
        print("⚠️  Installing schedule package...")
        os.system("pip install schedule")

    main()
