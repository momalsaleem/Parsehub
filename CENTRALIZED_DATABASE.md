# Centralized Database Configuration

## Overview

All files in this project now use a **single, centralized database file** configured through environment variables. This ensures data consistency across all components.

---

## Database Location

**Main Database File:** `backend/parsehub.db`

This is configured as `DATABASE_PATH` in the environment and used by:
- ✅ Backend API (Flask)
- ✅ Data ingestion scripts
- ✅ Test scripts
- ✅ Diagnostic tools
- ✅ All Python utilities

---

## How It Works

### 1. Environment Configuration

The database path is defined in **two places** (they sync automatically):

**`.env` (Root Directory)**
```env
DATABASE_PATH=backend/parsehub.db
```

**`backend/.env` (Backend Directory)**  
```env
DATABASE_PATH=backend/parsehub.db
```

### 2. Central Config Module

**`database_config.py`** (Root Directory)

This module reads the database path from environment variables and provides it to all scripts:

```python
from database_config import DATABASE_PATH

# Use it in any Python file
db = sqlite3.connect(DATABASE_PATH)
```

### 3. Backend Database Class

**`backend/database.py`**

The main database class now:
1. Reads `DATABASE_PATH` from environment
2. Falls back to `backend/parsehub.db` if not set
3. Converts relative paths to absolute paths automatically

```python
from backend.database import ParseHubDatabase

db = ParseHubDatabase()  # Uses configured DATABASE_PATH automatically
```

---

## Updated Files

All these files now use the centralized database configuration:

### Direct Database Access Files:
- ✅ `check_database_content.py` 
- ✅ `show_products.py`
- ✅ `view_metadata.py`
- ✅ `init_scraping_tables.py`
- ✅ `create_test_session.py`
- ✅ `comprehensive_check.py`

### Files Using Backend Class:
- ✅ `backend/database.py` (Main database class)
- ✅ `backend/api_server.py` (Flask API)
- ✅ Data ingestion scripts
- ✅ Test scripts

---

## Usage Examples

### Example 1: Using the Config Module

```python
from database_config import DATABASE_PATH
import sqlite3

# Directly use the centralized database path
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM product_data")
```

### Example 2: Using the Backend Class

```python
from backend.database import ParseHubDatabase

# Automatically uses the configured database
db = ParseHubDatabase()
conn = db.connect()
cursor = conn.cursor()
cursor.execute("SELECT * FROM product_data")
```

### Example 3: Scripts in Root Directory

```python
# Root script - uses DATABASE_PATH from .env
from database_config import DATABASE_PATH
import sqlite3

db = sqlite3.connect(DATABASE_PATH)
```

---

## To Change the Database Location

Edit **both** `.env` files:

1. **Root `.env`:**
   ```env
   DATABASE_PATH=/path/to/new/database.db
   ```

2. **Backend `.env`:**
   ```env
   DATABASE_PATH=/path/to/new/database.db
   ```

Or set environment variable before running:

```bash
# Windows
set DATABASE_PATH=path/to/database.db
python script.py

# Linux/Mac
export DATABASE_PATH=path/to/database.db
python script.py
```

---

## Database Current State

**Location:** `d:\Paramount Intelligence\ParseHub\Updated POC\Parsehub_project\backend\parsehub.db`

**Statistics:**
- Total Products: 629,690
- Projects: 105
- Runs: 185 processed
- Tables: 20+ 
- Records: 600,000+

---

## Verification

To verify all files are using the same database:

```bash
# Check database path being used
python -c "from database_config import DATABASE_PATH; print(f'Database: {DATABASE_PATH}')"

# Check database contents
python check_database_content.py

# Check specific project data
python show_products.py
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Environment Variables (.env files)                    │
│  DATABASE_PATH=backend/parsehub.db                     │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────────┐      ┌───────────────────────┐
│ database_config.py   │      │ backend/database.py   │
│ (Config Module)      │      │ (Main DB Class)       │
└──────────────────────┘      └───────────────────────┘
        │                             │
        │ Database Path              │ Database Path
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │                             │
        ▼                             ▼
   Test Scripts             Backend API + Services
   Diagnostic Tools         Data Ingestion Scripts
   Utility Scripts          All Python Utilities
        │                             │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ Single Database File        │
        │ backend/parsehub.db         │
        │                             │
        │ • 629,690 products          │
        │ • 105 projects              │
        │ • 185 runs processed        │
        │ • 20+ tables                │
        └─────────────────────────────┘
```

---

## Best Practices

✅ **Always use** `database_config.DATABASE_PATH` for hardcoded database access
✅ **Always use** `ParseHubDatabase()` for backend/service code
✅ **Keep both .env files** in sync with same `DATABASE_PATH`
✅ **Never hardcode** database paths in scripts
✅ **Always load environment** variables at script start
✅ **Use absolute paths** internally (config handles conversion)

---

## Migration Guide

If you need to move the database to a different location:

1. **Decide new location** (e.g., `/data/parsehub.db`)

2. **Update both .env files:**
   ```bash
   # Root .env
   DATABASE_PATH=/data/parsehub.db
   
   # Backend .env
   DATABASE_PATH=/data/parsehub.db
   ```

3. **Move the database file:**
   ```bash
   # Copy/move from current location
   cp backend/parsehub.db /data/parsehub.db
   ```

4. **Restart all services:**
   ```bash
   # Stop backend
   # Restart backend with new database path
   python backend/api_server.py
   ```

5. **Verify:**
   ```bash
   python check_database_content.py
   # Should show all 629,690 products
   ```

---

## Summary

✅ **One database file** used everywhere: `backend/parsehub.db`
✅ **Centralized configuration** via `.env` files
✅ **Automatic path conversion** handles relative/absolute paths
✅ **Backend class** provides safe database access
✅ **All scripts updated** to use centralized config
✅ **Easy to change** - just update .env files

**All 629,690 products are stored in one unified database that all scripts use consistently!** 🎉
