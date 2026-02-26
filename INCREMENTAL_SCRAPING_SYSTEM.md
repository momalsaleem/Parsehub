# Incremental Scraping System - Implementation Guide

## Overview

The Incremental Scraping System automatically manages projects that need continuation scraping based on metadata. It:

1. **Matches** project IDs from the `projects` table with the `metadata` table
2. **Compares** total pages (from metadata) with pages already scraped
3. **Automatically triggers** continuation runs for incomplete projects
4. **Updates** metadata with new page counts after successful runs
5. **Runs on a schedule** (configurable interval, default 30 minutes)

## How It Works

### System Flow

```
┌─────────────────────────────────────────────────┐
│  Incremental Scraping Scheduler (runs every 30m)│
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Check all projects in metadata                 │
│  Match project_id with projects table           │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  For each project:                              │
│  IF current_page_scraped < total_pages THEN     │
│    Calculate next page number                   │
│    Create continuation run                      │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Trigger ParseHub run from next page            │
│  Modify URL for pagination                      │
│  Store run info in database                     │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│  Monitor running continuation runs              │
│  Check completion status                        │
│  Update metadata with new page count            │
└─────────────────────────────────────────────────┘
```

### Database Schema

**Metadata Table**:
```sql
CREATE TABLE metadata (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    project_token TEXT UNIQUE,
    project_name TEXT,
    total_pages INTEGER,              -- Total pages to scrape
    current_page_scraped INTEGER,     -- Pages already scraped
    ...
)
```

**Runs Table**:
```sql
CREATE TABLE runs (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    run_token TEXT UNIQUE,
    status TEXT,
    pages_scraped INTEGER,
    is_continuation BOOLEAN,          -- TRUE for continuation runs
    ...
)
```

## New Files Created

### 1. `backend/incremental_scraping_manager.py`
Core service that handles all incremental scraping logic:
- Matches project IDs between tables
- Calculates next page numbers
- Triggers continuation runs
- Modifies URLs for pagination
- Monitors running continuations
- Updates metadata after completion

**Key Methods**:
- `check_and_match_pages()` - Main logic for checking incomplete projects
- `trigger_continuation_run()` - Starts a continuation run
- `modify_url_for_page()` - Handles pagination URL modifications
- `monitor_continuation_runs()` - Checks status of active runs
- `update_metadata_pages()` - Updates page counts after completion

### 2. `backend/incremental_scraping_scheduler.py`
Scheduler that runs the manager at regular intervals:
- Runs in background thread
- Configurable check interval (default 30 minutes)
- Can be started/stopped via API or code
- Handles exceptions gracefully

**Key Classes**:
- `IncrementalScrapingScheduler` - Main scheduler class
- Functions to start/stop scheduler globally

## API Endpoints

### 1. Check and Continue Scraping
```http
POST /api/scraping/check-and-continue
Authorization: Bearer <BACKEND_API_KEY>
```

Manually trigger the check for incomplete projects and start continuation runs.

**Response**:
```json
{
  "status": "success",
  "message": "Scheduled 3 continuation runs",
  "continuation_runs": [
    {
      "project_id": 1,
      "project_name": "MANN FILTER",
      "start_page": 5,
      "end_page": 10,
      "run_token": "abc123...",
      "status": "scheduled"
    }
  ]
}
```

### 2. Monitor Continuation Runs
```http
GET /api/scraping/monitor-continuations
Authorization: Bearer <BACKEND_API_KEY>
```

Check status of all running continuation runs and update their status.

**Response**:
```json
{
  "status": "success",
  "message": "Monitored continuation runs"
}
```

### 3. Get Scraping Status
```http
GET /api/scraping/project/<project_id>/status
```

Get the scraping status of a specific project.

**Response**:
```json
{
  "status": "success",
  "project_id": 1,
  "project_name": "MANN FILTER",
  "project_token": "abc123...",
  "total_pages": 10,
  "pages_scraped": 5,
  "pages_remaining": 5,
  "completion_percentage": 50.0,
  "is_complete": false
}
```

### 4. Get Incomplete Projects
```http
GET /api/scraping/projects/incomplete
```

Get list of all projects with incomplete scraping.

**Response**:
```json
{
  "status": "success",
  "incomplete_count": 3,
  "projects": [
    {
      "project_id": 1,
      "project_token": "abc123...",
      "project_name": "MANN FILTER",
      "total_pages": 10,
      "pages_scraped": 3,
      "pages_remaining": 7,
      "completion_percentage": 30.0
    }
  ]
}
```

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Backend Configuration
BACKEND_PORT=5000
BACKEND_API_KEY=t_hmXetfMCq3

# Incremental Scraping Configuration
# Check interval in minutes (how often to check for incomplete projects)
INCREMENTAL_SCRAPING_INTERVAL=30
```

### Starting the Scheduler

The scheduler **automatically starts** when the API server starts:

```bash
cd backend
python api_server.py
```

It will:
1. Read `INCREMENTAL_SCRAPING_INTERVAL` from environment (default 30 minutes)
2. Start background scheduler thread
3. Run first check after the configured interval
4. Continue checking at the specified interval

### Manual Startup (Standalone)

Run the scheduler independently:

```bash
cd backend
python incremental_scraping_scheduler.py 30
```

Arguments:
- `30` (optional) - Check interval in minutes (default 30)

### Adjusting Check Interval

To change how often the system checks for incomplete projects:

```bash
# Edit .env
INCREMENTAL_SCRAPING_INTERVAL=15  # Check every 15 minutes

# Restart the API server
python api_server.py
```

## URL Pagination Support

The system supports common pagination patterns:

### Supported Patterns

1. **Query Parameter - page**
   - Original: `https://example.com/products`
   - Page 5: `https://example.com/products?page=5`

2. **Query Parameter - p**
   - Original: `https://example.com/products`
   - Page 5: `https://example.com/products?p=5`

3. **Query Parameter - offset**
   - Original: `https://example.com/products`
   - Page 5: `https://example.com/products?offset=80` (assuming 20 items per page)

4. **Path-based Pagination**
   - Original: `https://example.com/products`
   - Page 5: `https://example.com/products?page=5`

### Custom Pagination

For websites with custom pagination patterns, modify the `modify_url_for_page()` method in `incremental_scraping_manager.py`:

```python
def modify_url_for_page(self, url: str, page_number: int) -> str:
    # Add your custom logic here
    # Example: https://example.com/products-page-5/
    if '/products' in url:
        base = url.split('?')[0]
        return f"{base}-page-{page_number}/"
    
    # Fall back to default logic
    return f"{url}?page={page_number}"
```

## Database Flow

### 1. Initial State
```sql
-- Metadata table has total_pages
SELECT project_id, total_pages, current_page_scraped 
FROM metadata 
WHERE project_id = 1;
-- Result: 1, 10, 3  (Total 10 pages, 3 already scraped)

-- Runs table has scraped data
SELECT pages_scraped FROM runs 
WHERE project_id = 1 AND status = 'completed';
-- Result: 3 (3 pages from previous runs)
```

### 2. Continuation Check
```
1. Check: current_page_scraped (3) < total_pages (10)? YES
2. Next page to start: 3 + 1 = 4
3. Schedule run from page 4-10 (7 pages remaining)
```

### 3. Run Execution
```
1. Create continuation run record (is_continuation = 1)
2. Trigger ParseHub with modified URL (page 4)
3. Monitor run status
4. When completed: update metadata
```

### 4. After Completion
```sql
-- Update metadata with new page count
UPDATE metadata 
SET current_page_scraped = 7  -- 3 + 4 pages scraped
WHERE project_id = 1;

-- Check current status
SELECT current_page_scraped FROM metadata WHERE project_id = 1;
-- Result: 7 (will continue from page 8 next time if needed)
```

## Usage Examples

### Example 1: Manual Check and Start Continuation

```bash
# Make API request to trigger manual check
curl -X POST http://localhost:5000/api/scraping/check-and-continue \
  -H "Authorization: Bearer t_hmXetfMCq3"
```

### Example 2: Check Project Status

```bash
# Get status of project 1
curl http://localhost:5000/api/scraping/project/1/status

# Example response:
# {
#   "status": "success",
#   "total_pages": 10,
#   "pages_scraped": 5,
#   "pages_remaining": 5,
#   "completion_percentage": 50.0
# }
```

### Example 3: Find All Incomplete Projects

```bash
# Get all projects that need continuation
curl http://localhost:5000/api/scraping/projects/incomplete

# Example response:
# {
#   "incomplete_count": 3,
#   "projects": [
#     {
#       "project_name": "MANN FILTER",
#       "pages_remaining": 7,
#       "completion_percentage": 30.0
#     },
#     ...
#   ]
# }
```

### Example 4: Python Integration

```python
from backend.incremental_scraping_manager import IncrementalScrapingManager

# Create manager
manager = IncrementalScrapingManager()

# Check all projects and start continuations
results = manager.check_and_match_pages()
print(f"Started {len(results)} continuation runs")

# Monitor running continuations
manager.monitor_continuation_runs()
```

## Logs and Monitoring

### Log Output

When the scheduler runs, you'll see output like:

```
================================================================================
[2026-02-20 14:30:00] Running incremental scraping check...
================================================================================

Project: MANN FILTER (ID: 1, Token: XBO0...)
Metadata: 3/10 pages scraped
Database: 3 pages from completed runs
Difference: 7 pages remaining

→ Scheduling continuation from page 4
  Remaining pages to scrape: 7
  ✓ Run scheduled successfully

Project: DOMETIC (ID: 2, Token: tXO1...)
Metadata: 8/8 pages scraped
✓ Project is complete (all 8 pages scraped)

================================================================================
✓ Scheduled 1 continuation runs
Next check: 2026-02-20 15:00:00
```

### Checking Continuation Runs

```sql
-- Check continuation runs
SELECT id, project_id, run_token, status, pages_scraped, is_continuation
FROM runs
WHERE is_continuation = 1
ORDER BY created_at DESC;
```

## Troubleshooting

### Issue: Continuation runs not triggering

1. **Check configuration**:
   ```bash
   # Verify environment variables
   echo $INCREMENTAL_SCRAPING_INTERVAL
   # Should output a number (default 30)
   ```

2. **Check database connection**:
   ```python
   from backend.database import ParseHubDatabase
   db = ParseHubDatabase()
   conn = db.connect()
   # If no error, database is working
   ```

3. **Check projects table**:
   ```sql
   SELECT COUNT(*) FROM projects;
   SELECT COUNT(*) FROM metadata;
   -- Both should have data
   ```

### Issue: URLs not being modified correctly

Check the pagination pattern of your target website and adjust `modify_url_for_page()`:

```python
# Test URL modification
manager = IncrementalScrapingManager()
url = "https://example.com/products"
new_url = manager.modify_url_for_page(url, 5)
print(new_url)  # Should show modified URL
```

### Issue: Runs completing but metadata not updating

Check the database connection and run completion status:

```sql
-- Check run status
SELECT status FROM runs 
WHERE project_id = 1 AND is_continuation = 1
ORDER BY created_at DESC
LIMIT 1;

-- Should be 'completed' when finished
```

## Testing

### Test 1: Check System Health

```bash
curl http://localhost:5000/api/health
# Should return: {"status": "healthy", "timestamp": "..."}
```

### Test 2: Manual Trigger

```bash
curl -X POST http://localhost:5000/api/scraping/check-and-continue \
  -H "Authorization: Bearer t_hmXetfMCq3"
# Should start continuation runs if any projects are incomplete
```

### Test 3: Check Incomplete Projects

```bash
curl http://localhost:5000/api/scraping/projects/incomplete
# Should list all projects that need continuation
```

## Performance Considerations

- **Check Interval**: Default 30 minutes balances responsiveness with system load
- **Database Queries**: Indexed queries for efficient lookups
- **URL Modifications**: Supports common pagination patterns without external dependencies
- **Continuation Runs**: Multiple projects can run simultaneously on ParseHub
- **Memory Usage**: Scheduler uses minimal resources with background thread

## Future Enhancements

1. **Smart Pagination**: Detect pagination pattern automatically
2. **Error Recovery**: Handle failed continuation runs gracefully
3. **Metrics Dashboard**: Real-time scraping progress visualization
4. **Webhook Notifications**: Alert when projects complete
5. **Batch Continuations**: Group small projects for efficiency
6. **Smart Scheduling**: Adjust check interval based on project activity

## Support

For issues or questions:
1. Check logs: Look for error messages in console output
2. Verify configuration: Check .env files
3. Test manually: Use API endpoints to test individual components
4. Check database: Verify data in metadata and runs tables

---

**Version**: 1.0  
**Last Updated**: 2026-02-20  
**Status**: Production Ready
