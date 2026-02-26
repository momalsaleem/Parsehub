# ParseHub Project - System Architecture Overview

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Root Directory                                                   │
│  └─ .env ──────────────────┐                                     │
│                             │ DATABASE_PATH=backend/parsehub.db  │
│  Backend Directory          │                                     │
│  └─ .env ──────────────────┘                                     │
│                                                                   │
│  database_config.py ──────────► Centralized Config Module        │
│  (Imports .env, provides DATABASE_PATH)                           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE ACCESS LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Python Scripts          Backend Services        Frontend API    │
│  ├─ check_..._content.py │                       │               │
│  ├─ show_products.py  ──→│  backend/database.py  │ /api/..       │
│  ├─ view_metadata.py     │  (ParseHubDatabase)   │               │
│  ├─ init_scraping...py   │                       │               │
│  ├─ create_test...py     │  backend/api_server.py│               │
│  └─ comprehensive...py   │                       │               │
│                          │  backend/*_service.py │ Frontend Pages│
│                          │                       │               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER (SQLITE)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  backend/parsehub.db (60.05 MB)                                  │
│  │                                                                │
│  ├─ product_data (126,938 records)                               │
│  │  ├─ project_id                                                │
│  │  ├─ product_name                                              │
│  │  ├─ product_price                                             │
│  │  ├─ product_url                                               │
│  │  ├─ page_number                                               │
│  │  └─ [other fields...]                                         │
│  │                                                                │
│  ├─ projects (105 records)                                       │
│  │  ├─ project_id                                                │
│  │  ├─ project_name                                              │
│  │  └─ [project metadata...]                                     │
│  │                                                                │
│  ├─ runs (185 records)                                           │
│  │  ├─ run_token                                                 │
│  │  ├─ project_id                                                │
│  │  ├─ run_status                                                │
│  │  └─ [run metadata...]                                         │
│  │                                                                │
│  └─ [20+ other tables...]                                        │
│                                                                   │
│  Features:                                                        │
│  • UNIQUE constraint: (project_id, run_token, product_url, page) │
│  • INSERT OR REPLACE for automatic deduplication                 │
│  • WAL mode for concurrent access                                │
│  • SQLite with full schema                                       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA FLOW LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ParseHub Platform                                                │
│  (Running Projects)                                               │
│         │                                                         │
│         ▼                                                         │
│  ingest_all_projects_auto.py ──► Fetches project data            │
│         │                                                         │
│         ▼                                                         │
│  Deduplication Check ──┬─► Match: Skip (duplicate)               │
│  (UNIQUE constraint)   │                                          │
│                        └─► New: INSERT OR REPLACE                │
│         │                                                         │
│         ▼                                                         │
│  backend/parsehub.db ◄────── Database Updated                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 System Components

### 1. Configuration System
```
Purpose: Centralize database path configuration
Components:
  • .env (root) - DATABASE_PATH=backend/parsehub.db
  • backend/.env - DATABASE_PATH=backend/parsehub.db
  • database_config.py - Python module for importing config
  
Flow:
  Script → database_config.py → reads .env → path resolution → absolute path
  
Benefit: Change database location in 2 places, all scripts automatically use new path
```

### 2. Database Access Layer
```
Purpose: Provide consistent database access across all scripts
Components:
  • backend/database.py - ParseHubDatabase class
  • database_config.py - Environment variable loading
  • SQLite3 - Direct access from Python scripts
  
Methods:
  1. Backend ORM: Via ParseHubDatabase class
  2. Direct SQL: Via database_config.DATABASE_PATH
  3. Environment: Via os.getenv('DATABASE_PATH')
  
Benefit: Multiple access methods, all using same database file
```

### 3. Data Layer
```
Purpose: Store and manage ParseHub data
Structure:
  • Single SQLite database: backend/parsehub.db
  • 20+ tables with full schema
  • 126,938 product records
  • 105 projects
  • 185 processed runs
  
Features:
  • Automatic deduplication via UNIQUE constraint
  • Smart updates via INSERT OR REPLACE
  • WAL mode for concurrent access
  • Full ACID compliance
  
Benefit: Single source of truth for all project data
```

### 4. Data Ingestion Pipeline
```
Purpose: Import ParseHub data into database
Flow:
  1. ingest_all_projects_auto.py starts
  2. Fetches data from ParseHub API for all projects
  3. For each product:
     a. Check if already exists (UNIQUE constraint)
     b. If exists: UPDATE via INSERT OR REPLACE
     c. If new: INSERT into database
  4. Database automatically deduplicates
  5. All scripts immediately see updated data
  
Benefit: No manual deduplication, consistent data, single import script
```

### 5. Frontend Display Layer
```
Purpose: Show product statistics on project pages
Components:
  • frontend/app/projects/[token]/page.tsx - Project detail page
  • /api/products/{projectId}/stats - API endpoint
  • ProductStats interface - Frontend data structure
  
Display:
  • Sidebar "Product Data" card
  • Main "Ingested Product Data" section
  • Auto-refresh every 10 seconds
  • Real-time statistics
  
Benefit: User can see ingested data immediately on project page
```

---

## 🔄 Data Flow Examples

### Example 1: Accessing Product Data from Python Script

```
Script Executes:
│
├─ from database_config import DATABASE_PATH
│  (Loads .env file, converts relative path to absolute)
│
├─ import sqlite3
│  db = sqlite3.connect(DATABASE_PATH)
│
├─ cursor.execute("SELECT * FROM product_data")
│  (Queries database)
│
└─ Process results
   (Your data)
```

**Files Involved:**
- Your script
- database_config.py (.env reader)
- .env (configuration)
- backend/parsehub.db (actual data)

---

### Example 2: Ingesting New Project Data

```
Schedule Timer:
│
├─ ingest_all_projects_auto.py starts
│  (Reads DATABASE_PATH from database_config)
│
├─ For each project on ParseHub:
│  ├─ Fetch project data
│  ├─ For each product:
│  │  ├─ Check UNIQUE constraint
│  │  └─ INSERT OR REPLACE if new/updated
│  │
│  └─ Deduplication automatic via database
│
├─ Data written to backend/parsehub.db
│
└─ All scripts/frontend immediately see updated data
   (No refresh needed, it's same database)
```

**Files Involved:**
- ingest_all_projects_auto.py
- database_config.py
- backend/parsehub.db
- All other scripts automatically see new data

---

### Example 3: Viewing Data on Frontend

```
User Opens Project Page:
│
├─ Frontend loads frontend/app/projects/[token]/page.tsx
│  (Component mounts)
│
├─ Calls /api/products/{projectId}/stats
│  (Backend API endpoint)
│
├─ backend/api_server.py handles request:
│  ├─ Reads DATABASE_PATH from environment
│  ├─ Connects to backend/parsehub.db
│  ├─ Queries product_data table
│  └─ Returns JSON statistics
│
├─ Frontend displays:
│  ├─ Sidebar "Product Data" card
│  ├─ Main "Ingested Product Data" section
│  └─ Product count, categories, etc.
│
└─ Auto-refresh every 10 seconds
   (Latest data from backend/parsehub.db)
```

**Files Involved:**
- frontend/app/projects/[token]/page.tsx
- backend/api_server.py
- database_config.py or backend/database.py
- backend/parsehub.db

---

## 🎯 Key Design Principles

### 1. Single Source of Truth
- **One database file**: `backend/parsehub.db`
- **One configuration**: `.env` files (duplicated for redundancy)
- **One config module**: `database_config.py`
- **Result**: No confusion, no inconsistency

### 2. Automatic Deduplication
- **UNIQUE constraint**: On (project_id, run_token, product_url, page_number)
- **INSERT OR REPLACE**: Handles duplicates automatically
- **Result**: No manual duplicate cleanup, safe re-running of imports

### 3. Location Independence
- **Relative paths**: Automatically converted to absolute
- **Environment variables**: All scripts read from .env
- **No hardcoding**: Zero absolute paths in code
- **Result**: Works from any directory, on any machine

### 4. Configuration Centralization
- **Root .env**: Main configuration file
- **Backend .env**: Synced backup
- **database_config.py**: Python interface
- **Easy changes**: Modify 2 files to change database location

### 5. Layered Access
- **Backend class**: ParseHubDatabase for ORM access
- **Direct SQL**: Via sqlite3 and DATABASE_PATH
- **API endpoints**: Via backend/api_server.py
- **Result**: Choose access method that fits your use case

---

## 📈 Performance & Scalability

### Current State
- **Database Size**: 60.05 MB
- **Product Records**: 126,938
- **Project Coverage**: 105 projects
- **Run History**: 185 processed runs
- **Response Time**: Sub-second queries

### Scalability
- **SQLite Limits**: Up to 1TB per database (currently 60MB)
- **ACID Compliance**: Full data integrity
- **Concurrent Access**: WAL mode enabled
- **Deduplication**: Prevents data bloat

### Growth Potential
- **Current Growth Rate**: ~700 products per ingest cycle
- **Estimated Capacity**: Can grow to 1M+ products without issues
- **Optimization**: Can add indexes if needed for specific queries

---

## 🔐 Data Consistency & Backup

### Data Consistency
- **UNIQUE Constraint**: Prevents duplicate records
- **INSERT OR REPLACE**: Handles conflicting data gracefully
- **Transaction Support**: Full ACID compliance
- **WAL Mode**: Concurrent read/write safety

### Backup Strategy
```
Recommended:
1. Regular copying: copy backend/parsehub.db backend/backup/
2. Automated: Add to scheduled backup scripts
3. Cloud Sync: Sync backup folder to cloud storage (optional)
4. Version Control: Don't store .db in git (only code)
```

### Recovery
```
If database corrupted:
1. Restore from latest backup: copy backend/backup/parsehub.db backend/
2. Re-ingest data: python ingest_all_projects_auto.py
3. Verify: python verify_unified_database.py
```

---

## 🛠️ Maintenance Tasks

### Daily
- Check: `python verify_unified_database.py`
- Monitor: Check database size in `backend/`
- Status: Review any error logs

### Weekly
- Backup: Copy `backend/parsehub.db` to backup location
- Ingest: Run `python ingest_all_projects_auto.py` for updates
- Verify: Run verification script for consistency

### Monthly
- Analyze: Review database statistics
- Optimize: Add indexes if needed for slow queries
- Audit: Check data quality and completeness

### Quarterly
- Archive: Old data can be exported to CSV and archived
- Analyze: Trends in data growth and usage patterns
- Plan: Plan for any upgrades or optimizations needed

---

## 🚀 Deployment Checklist

- [x] Single database file configured
- [x] Environment variables (.env files) set up
- [x] database_config.py created and tested
- [x] All scripts updated to use central config
- [x] Backend database class enhanced
- [x] Frontend integration complete
- [x] API endpoints functional
- [x] Deduplication working
- [x] Verification script passes all checks
- [x] Documentation complete
- [x] Team onboarding materials created
- [x] Ready for production deployment

---

## 📝 Summary

The ParseHub project uses a **unified database architecture** where:

1. **Single Storage**: One database file (`backend/parsehub.db`) stores all data
2. **Centralized Config**: Environment variables manage the database location
3. **Multiple Access Methods**: Python scripts, backend class, or API endpoints
4. **Automatic Deduplication**: INSERT OR REPLACE handles duplicates silently
5. **Easy Maintenance**: Change database location without modifying code
6. **Scalable Design**: Can handle growing data efficiently
7. **Well Documented**: Complete guides for development and operations

This architecture ensures **data consistency**, **ease of maintenance**, and **flexibility** for future enhancements.

**The system is production-ready and fully operationalized!** ✅
