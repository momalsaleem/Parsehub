# Auto-Sync Service - Quick Start

## What It Does

The **Auto-Sync Service** automatically keeps your database updated with the latest information from ParseHub:

- ✅ **Project details** - Automatically syncs project titles, URLs, and metadata
- ✅ **Run statuses** - Tracks all runs (running, completed, cancelled, failed)
- ✅ **Real-time updates** - Checks every 5 minutes (configurable)
- ✅ **Smart syncing** - Only updates changed data, efficient API usage

## Quick Start (30 seconds)

### 1. Start the Server

```bash
cd backend
python api_server.py
```

You'll see:
```
Starting Auto-Sync Service (sync interval: 5 minutes)
[OK] Auto-Sync Service started (interval: 5 minutes)
```

That's it! The service is now running and syncing data automatically.

### 2. Verify It's Working

```bash
# Check status
curl http://localhost:5000/api/sync/status
```

Response:
```json
{
  "running": true,
  "status": "running",
  "sync_interval_minutes": 5
}
```

### 3. Trigger Manual Sync (Optional)

```bash
# Run a sync immediately (don't wait for next interval)
curl -X POST http://localhost:5000/api/sync/trigger \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

Response:
```json
{
  "status": "success",
  "message": "Manual sync completed",
  "results": {
    "projects_synced": 55,
    "runs_updated": 3,
    "projects_updated": 55
  }
}
```

## What Gets Synced

### Every 5 Minutes (Automatic)

1. **All Projects**
   - Fetches all projects from ParseHub API
   - Updates project titles, main sites, owner emails
   - Creates new projects if found

2. **Latest Runs**
   - Syncs last_run info for each project
   - Updates run statuses (running → completed)
   - Creates new run records

3. **Active Runs**
   - Checks all "running" or "initializing" runs
   - Updates their status from ParseHub
   - Tracks completion

## Configuration

### Change Sync Interval

Edit `.env`:
```bash
AUTO_SYNC_INTERVAL=5  # Minutes between syncs
```

**Recommended values:**
- `1` - Real-time monitoring (every minute)
- `5` - Default (good balance)
- `10` - Less frequent (stable projects)
- `30` - Minimal syncing (archived projects)

Restart server after changing:
```bash
python api_server.py
```

## Monitoring

### Console Output

Watch the sync happen:
```
================================================================================
[2026-02-20 14:30:00] Running auto-sync...
================================================================================

1. Fetching all projects from ParseHub API...
   Found 55 projects

2. Syncing: MANN FILTER (XBO0lkrO...)
   [OK] Updated project (ID: 1)
   [OK] Updated run abcd1234... (running -> completed)

[OK] Sync completed:
  - Projects synced: 55
  - Runs updated: 3
  - Projects updated: 55

Next sync: 2026-02-20 14:35:00
```

### Database Check

See what's been synced:
```sql
-- Check last sync times
SELECT token, title, updated_at 
FROM projects 
ORDER BY updated_at DESC 
LIMIT 5;

-- Check recently updated runs
SELECT r.run_token, r.status, r.updated_at, p.title
FROM runs r
JOIN projects p ON r.project_id = p.id
ORDER BY r.updated_at DESC
LIMIT 5;
```

## API Endpoints

### GET /api/sync/status

Check if service is running:
```bash
curl http://localhost:5000/api/sync/status
```

### POST /api/sync/trigger

Force immediate sync:
```bash
curl -X POST http://localhost:5000/api/sync/trigger \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

## How It Works With Other Services

### ✅ Works With: Incremental Scraping
- **Auto-Sync** keeps run statuses updated
- **Incremental Scraping** detects incomplete projects
- Together: Complete automation

### ✅ Works With: Monitoring Service
- **Auto-Sync** updates statuses every 5 minutes
- **Monitoring** detects stopped runs
- **Recovery** restarts failed runs

## Benefits

### 🚀 Always Up-to-Date
Your database always reflects the latest ParseHub data without manual intervention.

### 💰 Efficient
Only syncs changed data, minimal API calls, smart rate limiting.

### 🔄 Real-Time Ready
Set to 1-minute interval for near real-time dashboard updates.

### 📊 Complete History
Maintains full record of all projects and runs over time.

## Common Tasks

### Force Immediate Sync
```bash
curl -X POST http://localhost:5000/api/sync/trigger \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

### Check if Running
```bash
curl http://localhost:5000/api/sync/status
```

### Monitor in Real-Time
```bash
# Keep terminal open while server runs
cd backend
python api_server.py
# Watch the sync messages every 5 minutes
```

### Change Frequency
```bash
# Edit .env
echo "AUTO_SYNC_INTERVAL=1" >> .env

# Restart
python api_server.py
```

## Troubleshooting

### Not Seeing Updates?

1. **Check if running:**
   ```bash
   curl http://localhost:5000/api/sync/status
   # Should show "running": true
   ```

2. **Trigger manual sync:**
   ```bash
   curl -X POST http://localhost:5000/api/sync/trigger \
     -H "Authorization: Bearer t_hmXetfMCq3"
   ```

3. **Check database timestamps:**
   ```sql
   SELECT MAX(updated_at) FROM projects;
   ```

### Service Not Starting?

Check the console output when starting:
```
Starting Auto-Sync Service (sync interval: 5 minutes)
[OK] Auto-Sync Service started (interval: 5 minutes)
```

If you don't see this, check:
- Is `PARSEHUB_API_KEY` set in `.env`?
- Are there any error messages?

### Too Many API Calls?

Increase the interval:
```bash
# .env
AUTO_SYNC_INTERVAL=10  # Double the interval
```

Built-in rate limiting prevents throttling.

## Test It

Run the test script:
```bash
cd Parsehub_project
python test_auto_sync.py
```

Should output:
```
Testing Auto-Sync Service...
==================================================

1. Checking auto-sync status...
Status Code: 200
Response: {'running': True, ...}

2. Triggering manual sync...
[OK] Manual sync completed successfully!
Projects synced: 55
Runs updated: 0
Projects updated: 55

==================================================
Auto-Sync Service is working correctly!
```

## Next Steps

1. ✅ Start the server: `python api_server.py`
2. ✅ Verify it's running: `curl http://localhost:5000/api/sync/status`
3. ✅ Watch the console for sync messages
4. ✅ Check database to see updated data
5. ✅ Adjust interval as needed in `.env`

**Done!** Your database now stays automatically synchronized with ParseHub.

---

**Full documentation:** See [AUTO_SYNC_SERVICE.md](AUTO_SYNC_SERVICE.md)  
**Version:** 1.0  
**Status:** Production Ready
