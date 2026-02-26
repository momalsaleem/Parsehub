# Incremental Scraping System - Quick Start Guide

## 5-Minute Setup

### 1. Start the System
```bash
cd backend
python api_server.py
```

You should see:
```
Starting Incremental Scraping Scheduler (check interval: 30 minutes)
Flask API server running on http://localhost:5000
```

The scheduler is now running in the background, checking every 30 minutes for incomplete projects.

### 2. Test It's Working
```bash
# Check if there are incomplete projects
curl http://localhost:5000/api/scraping/projects/incomplete

# Or trigger a manual check immediately
curl -X POST http://localhost:5000/api/scraping/check-and-continue \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

### 3. Check Results
```bash
# View project status
curl http://localhost:5000/api/scraping/project/1/status

# View all running continuation runs
curl http://localhost:5000/api/scraping/monitor-continuations
```

That's it! The system is now automatically continuing any incomplete projects.

## How It Works (Simple Version)

1. **Every 30 minutes** (or manually via API), the system:
   - Looks at all projects in the database
   - Checks how many pages were requested vs. how many were scraped
   - If pages are missing, schedules a continuation run

2. **For each incomplete project**:
   - Calculates the next page to scrape
   - Modifies the URL with the page number
   - Triggers a new ParseHub run

3. **When the run completes**:
   - Saves results to the database
   - Updates the page count
   - System ready to continue again if needed

## Common Tasks

### Check if System is Running
```bash
curl http://localhost:5000/api/health
```
Should return: `{"status": "healthy"}`

### See All Incomplete Projects
```bash
curl http://localhost:5000/api/scraping/projects/incomplete
```

### Check One Project's Status
```bash
curl http://localhost:5000/api/scraping/project/1/status
```

### Trigger Manual Check Now (Don't Wait 30min)
```bash
curl -X POST http://localhost:5000/api/scraping/check-and-continue \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

### Change Check Interval
Edit `.env` and change:
```bash
INCREMENTAL_SCRAPING_INTERVAL=15  # Check every 15 minutes instead
```
Then restart the server.

## Configuration Options

**`.env` File Variables**:
```bash
BACKEND_PORT=5000                      # Server port
BACKEND_API_KEY=t_hmXetfMCq3           # API authentication key
INCREMENTAL_SCRAPING_INTERVAL=30       # Check interval in minutes
```

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scraping/check-and-continue` | POST | Start checking and continue incomplete projects |
| `/api/scraping/projects/incomplete` | GET | List all incomplete projects |
| `/api/scraping/project/<id>/status` | GET | Check specific project status |
| `/api/scraping/monitor-continuations` | GET | Monitor running continuation runs |

All endpoints require:
```
Authorization: Bearer t_hmXetfMCq3
```

## Monitoring

Watch the console output when system is running:

```
[2026-02-20 14:30:00] Running incremental scraping check...

Project: MANN FILTER (ID: 1)
Metadata: 3/10 pages scraped
→ Scheduling continuation from page 4
✓ Run scheduled successfully

Project: DOMETIC (ID: 2)
Metadata: 8/8 pages scraped
✓ Project is complete

✓ Scheduled 1 continuation runs
Next check: 2026-02-20 15:00:00
```

## Files Involved

- **`incremental_scraping_manager.py`** - Handles project checking and run triggering
- **`incremental_scraping_scheduler.py`** - Runs checks in background
- **`api_server.py`** - API endpoints and scheduler startup
- **`.env`** - Configuration variables

## Troubleshooting

**Not seeing any continuation runs?**
1. Check if projects table has data: `SELECT COUNT(*) FROM projects`
2. Check if metadata table has data: `SELECT COUNT(*) FROM metadata`
3. Check if any projects are incomplete: `curl http://localhost:5000/api/scraping/projects/incomplete`

**Want to see what's happening?**
- Keep the console open while running
- Look for log messages showing which projects are checked
- Check database directly:
  ```bash
  sqlite3 backend/parsehub.db
  SELECT project_name, total_pages, current_page_scraped FROM metadata LIMIT 5;
  ```

**Need to adjust check interval?**
- Edit `.env`: `INCREMENTAL_SCRAPING_INTERVAL=15`
- Restart `python api_server.py`

## Next Steps

1. ✅ Start the server: `python api_server.py`
2. ✅ Monitor the logs for continuation runs
3. ✅ Check database to see updated page counts
4. ✅ Verify continuation runs complete successfully
5. ✅ Adjust interval as needed for your use case

Done! Your system is now automatically continuing incomplete projects.

**More details?** See [INCREMENTAL_SCRAPING_SYSTEM.md](INCREMENTAL_SCRAPING_SYSTEM.md) for full documentation.
