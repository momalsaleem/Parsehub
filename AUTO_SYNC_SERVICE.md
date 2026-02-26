# Auto-Sync Service - Automatic Database Updates from ParseHub

## Overview

The **Auto-Sync Service** automatically keeps your local database synchronized with the latest data from ParseHub API. It runs in the background and periodically fetches:

- **Project details** - Title, main site, owner email
- **Latest run information** - Status, pages scraped, timestamps
- **Active run updates** - Real-time status of running/pending runs

## How It Works

```
┌─────────────────────────────────────────────────┐
│  Auto-Sync Service (runs every 5 minutes)      │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  1. Fetch ALL projects from ParseHub API       │
│     (with pagination support)                   │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  2. For each project:                           │
│     - Update project details in database        │
│     - Sync last_run information                 │
│     - Create new records if needed              │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  3. Update all active runs:                     │
│     - Check runs marked as 'running'            │
│     - Fetch latest status from ParseHub         │
│     - Update database with new status           │
└─────────────────────────────────────────────────┘
```

## Key Features

### ✅ Automatic Updates
- Runs in background thread (daemon)
- Configurable sync interval (default: 5 minutes)
- No manual intervention needed

### ✅ Smart Syncing
- Only updates changed data
- Rate limiting to avoid API throttling
- Handles pagination for large project lists

### ✅ Comprehensive Coverage
- Projects: Title, owner, main site, last update
- Runs: Status, pages scraped, start/end times, duration
- Real-time tracking of active runs

### ✅ Database Integration
- Creates new projects if they don't exist
- Updates existing records
- Maintains referential integrity
- Tracks last update timestamps

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Auto-Sync Configuration
# Sync interval in minutes (how often to sync data from ParseHub API to database)
AUTO_SYNC_INTERVAL=5
```

**Recommended intervals:**
- **5 minutes** (default) - Good balance of freshness and API usage
- **1 minute** - Real-time updates (use for critical monitoring)
- **10 minutes** - Reduced API calls (use for stable/completed projects)
- **30 minutes** - Minimal API usage (use for archived projects)

## Starting the Service

### Automatic Start (with API Server)

The auto-sync service **automatically starts** when you run the API server:

```bash
cd backend
python api_server.py
```

You'll see:
```
Starting ParseHub API Server on port 5000
Starting Incremental Scraping Scheduler (check interval: 30 minutes)
Starting Auto-Sync Service (sync interval: 5 minutes)
```

### Standalone Mode

Run the service independently:

```bash
cd backend
python auto_sync_service.py 5
```

Arguments:
- `5` (optional) - Sync interval in minutes (default 5)

## API Endpoints

### 1. Manual Sync Trigger

Trigger an immediate sync without waiting for the next scheduled interval:

```http
POST /api/sync/trigger
Authorization: Bearer <BACKEND_API_KEY>
```

**Response:**
```json
{
  "status": "success",
  "message": "Manual sync completed",
  "results": {
    "projects_synced": 105,
    "runs_updated": 23,
    "projects_updated": 105
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/sync/trigger \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

### 2. Get Sync Status

Check if the auto-sync service is running:

```http
GET /api/sync/status
```

**Response (Running):**
```json
{
  "status": "running",
  "running": true,
  "sync_interval_minutes": 5
}
```

**Response (Stopped):**
```json
{
  "status": "stopped",
  "running": false
}
```

**Example:**
```bash
curl http://localhost:5000/api/sync/status
```

## What Gets Synced

### Projects Table

| Field | Source | Notes |
|-------|--------|-------|
| `token` | ParseHub API | Unique project identifier |
| `title` | ParseHub API | Project name |
| `owner_email` | ParseHub API | Project owner |
| `main_site` | ParseHub API | Target website |
| `updated_at` | System | Last sync timestamp |

### Runs Table

| Field | Source | Notes |
|-------|--------|-------|
| `run_token` | ParseHub API | Unique run identifier |
| `status` | ParseHub API | running/completed/cancelled/failed |
| `pages_scraped` | ParseHub API | Number of pages processed |
| `start_time` | ParseHub API | Run start timestamp |
| `end_time` | ParseHub API | Run completion timestamp |
| `duration_seconds` | Calculated | Difference between start and end |
| `updated_at` | System | Last sync timestamp |

## Sync Behavior

### New Projects
When a new project is found in ParseHub:
1. Creates new record in `projects` table
2. Syncs last_run information if available
3. Logs creation to console

### Existing Projects
For projects already in database:
1. Updates project details (title, main site, etc.)
2. Checks if last_run has changed
3. Updates or creates run records as needed

### Active Runs
For runs marked as "running" or "initializing":
1. Fetches latest status from ParseHub API
2. Updates status if changed
3. Updates pages_scraped count
4. Sets end_time when completed

## Monitoring

### Console Output

When auto-sync runs, you'll see output like:

```
================================================================================
[2026-02-20 14:30:00] Running auto-sync...
================================================================================

1. Fetching all projects from ParseHub API...
   Found 105 projects

2. Syncing: MANN FILTER (XBO0lkrO...)
   ✓ Updated project (ID: 1)
   ✓ Updated run abcd1234... (running → completed)

2. Syncing: DOMETIC (tXO1Km1c...)
   ✓ Updated project (ID: 2)

3. Updating active runs...
   Found 3 potentially active runs
   ✓ Updated run xyz789... (status: completed)

✓ Sync completed:
  - Projects synced: 105
  - Runs updated: 3
  - Projects updated: 105

Next sync: 2026-02-20 14:35:00
```

### Database Queries

Check last sync times:

```sql
-- Check when projects were last updated
SELECT token, title, updated_at 
FROM projects 
ORDER BY updated_at DESC 
LIMIT 10;

-- Check recently updated runs
SELECT r.run_token, r.status, r.updated_at, p.title
FROM runs r
JOIN projects p ON r.project_id = p.id
ORDER BY r.updated_at DESC
LIMIT 10;

-- Check active runs
SELECT r.run_token, r.status, p.title, r.start_time
FROM runs r
JOIN projects p ON r.project_id = p.id
WHERE r.status IN ('running', 'initializing')
ORDER BY r.start_time DESC;
```

## Integration with Other Services

### Works With Incremental Scraping

The auto-sync service complements the incremental scraping system:

1. **Auto-Sync** keeps run statuses updated
2. **Incremental Scraping** detects incomplete projects
3. Both work together to maintain complete data

### Works With Monitoring Service

The monitoring service can benefit from auto-sync:

1. **Auto-Sync** updates run statuses every 5 minutes
2. **Monitoring Service** detects stopped runs
3. **Recovery Service** can restart failed runs

## Use Cases

### 1. Real-Time Dashboard
- Set `AUTO_SYNC_INTERVAL=1` for minute-by-minute updates
- Display live run progress in frontend
- Track active scraping sessions

### 2. Project Management
- Keep project list always up-to-date
- Automatically discover new projects
- Track project modifications

### 3. Run History
- Maintain complete run history
- Track status changes over time
- Calculate success rates

### 4. Status Monitoring
- Detect when runs complete
- Alert on failed runs
- Track scraping performance

## Troubleshooting

### Service Not Starting

**Check environment variables:**
```bash
# Verify API key is set
echo $PARSEHUB_API_KEY
# Should output your API key

# Verify interval is set
echo $AUTO_SYNC_INTERVAL
# Should output a number (default 5)
```

**Check logs:**
```
✓ Auto-Sync Service started (interval: 5 minutes)
```

If you don't see this, the service didn't start.

### No Updates Happening

**Check service status:**
```bash
curl http://localhost:5000/api/sync/status
```

Should return `"running": true`.

**Trigger manual sync:**
```bash
curl -X POST http://localhost:5000/api/sync/trigger \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

Check the results to see if sync is working.

### API Rate Limiting

If you see errors about rate limiting:

1. **Increase sync interval:**
   ```bash
   AUTO_SYNC_INTERVAL=10  # Change to 10 minutes
   ```

2. **Restart the server:**
   ```bash
   python api_server.py
   ```

The service has built-in rate limiting (0.3-0.5 second delays between requests).

### Database Lock Errors

If you see "database is locked" errors:

1. The database uses WAL mode for better concurrency
2. Check if other processes are holding locks
3. Increase busy timeout in database.py (already set to 30 seconds)

## Performance Considerations

- **API Calls**: ~1 call per project + 1 call per active run per sync
- **Example**: 100 projects + 5 active runs = 105 API calls every sync
- **At 5-minute interval**: 105 calls every 5 minutes = 21 calls/minute
- **ParseHub limit**: Typically 1000+ calls/hour (well within limit)

## Advanced Configuration

### Custom Sync Logic

Modify [auto_sync_service.py](auto_sync_service.py) to customize:

```python
def sync_project(self, project: Dict, results: Dict):
    # Add custom sync logic here
    # Example: Only sync specific project types
    if project.get('title').startswith('PRIORITY'):
        # Priority sync
        pass
```

### Selective Syncing

Only sync certain projects:

```python
def sync_all(self):
    projects = self.fetch_all_projects()
    
    # Filter projects
    projects = [p for p in projects if condition(p)]
    
    for project in projects:
        self.sync_project(project, results)
```

### Data Transformations

Transform data before storing:

```python
def sync_run(self, project_id: int, run_data: Dict, results: Dict):
    # Transform status codes
    status = run_data.get('status', 'unknown')
    if status == 'complete':
        status = 'completed'  # Normalize status
    
    # Store normalized data
    cursor.execute(...)
```

## Best Practices

### ✅ DO:
- Keep sync interval reasonable (5-10 minutes for active projects)
- Monitor console output for errors
- Use manual trigger for immediate updates when needed
- Check sync status before troubleshooting
- Review database timestamps to verify syncing

### ❌ DON'T:
- Set interval too low (< 1 minute) unless necessary
- Disable auto-sync without reason
- Ignore error messages in logs
- Manually edit database during sync (may cause conflicts)

## FAQs

**Q: Does this replace the incremental scraping service?**  
A: No, they work together. Auto-sync updates data from ParseHub, while incremental scraping triggers new runs.

**Q: What happens if ParseHub API is down?**  
A: Service will log errors but continue running. It will retry on next sync interval.

**Q: Can I run this without the API server?**  
A: Yes, run standalone: `python auto_sync_service.py 5`

**Q: How do I know if sync is working?**  
A: Check `updated_at` timestamps in database, or watch console output.

**Q: Does this use a lot of API calls?**  
A: No, it's designed to be efficient with built-in rate limiting.

**Q: Can I sync on-demand?**  
A: Yes, use `POST /api/sync/trigger` endpoint.

---

**Version**: 1.0  
**Last Updated**: 2026-02-20  
**Status**: Production Ready
