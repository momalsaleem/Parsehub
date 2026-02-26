# ParseHub Project - Team Onboarding Checklist

This checklist helps new team members understand and work with the ParseHub unified database system.

## ✅ Understanding the System

- [ ] Read `README.md` for project overview
- [ ] Read `PROJECT_STATUS.md` for current system state
- [ ] Read `CENTRALIZED_DATABASE.md` for database architecture
- [ ] Read `QUICK_REFERENCE.md` for common commands
- [ ] Understand: **Single database file** is used everywhere (`backend/parsehub.db`)

## ✅ Environment Setup

- [ ] Navigate to project root directory:
  ```bash
  cd d:\Paramount Intelligence\ParseHub\Updated POC\Parsehub_project
  ```

- [ ] Verify Python is installed:
  ```bash
  python --version
  ```

- [ ] Verify `.env` file exists in root:
  ```bash
  type .env
  ```
  Should show: `DATABASE_PATH=backend/parsehub.db`

- [ ] Verify `database_config.py` exists:
  ```bash
  type database_config.py
  ```

## ✅ Verify System is Working

- [ ] Run the verification script:
  ```bash
  python verify_unified_database.py
  ```
  
- [ ] Check output shows:
  ```
  ✅ Both .env files use SAME DATABASE
  ✅ database_config.py imports successfully
  ✅ Database file exists
  ✅ Database contents verified
  ✅ ALL CHECKS PASSED
  ```

## ✅ Understanding the Database

### Key Facts
- [ ] Single database file: `backend/parsehub.db`
- [ ] Contains: 126,938 product records
- [ ] From: 105 projects
- [ ] In: 185 processed runs
- [ ] Configuration: Environment variables in `.env` files
- [ ] Deduplication: Automatic via UNIQUE constraint

### Database Structure
- [ ] Product data table: `product_data`
- [ ] Projects table: `projects`
- [ ] Runs table: `runs`
- [ ] Metadata tables: Multiple metadata-related tables
- [ ] All accessible via centralized `database_config.py`

## ✅ Accessing the Database

### Method 1: Using Config Module (Most Common)
```python
from database_config import DATABASE_PATH
import sqlite3

db = sqlite3.connect(DATABASE_PATH)
cursor = db.cursor()
cursor.execute("SELECT COUNT(*) FROM product_data")
print(cursor.fetchone()[0])
db.close()
```
- [ ] Understand this is the recommended approach
- [ ] Know that DATABASE_PATH is automatically resolved to absolute path

### Method 2: Using Backend Class
```python
from backend.database import ParseHubDatabase
db = ParseHubDatabase()
```
- [ ] Know the backend class handles database initialization
- [ ] Know it reads from the same environment configuration

## ✅ Common Daily Tasks

### Checking Database Status
- [ ] Run: `python check_database_content.py`
- [ ] Know this shows table counts and schema
- [ ] Know which tables contain your data

### Viewing Products
- [ ] Run: `python show_products.py`
- [ ] Know how to limit results
- [ ] Know the product schema

### Updating Data
- [ ] Understand: ParseHub projects run automatically
- [ ] Run: `python ingest_all_projects_auto.py` to import/update data
- [ ] Know: New data automatically replaces old data
- [ ] Know: Duplicates automatically handled

### Accessing Frontend
- [ ] URL: http://localhost:3000
- [ ] Project pages show product statistics
- [ ] Statistics auto-refresh every 10 seconds

## ✅ Important Configuration Files

### Root Directory
```
.env                          - Database path and config
database_config.py            - Config module for imports
verify_unified_database.py    - Verification script
PROJECT_STATUS.md             - Complete status document
CENTRALIZED_DATABASE.md       - Database guide
QUICK_REFERENCE.md           - Quick reference
```

- [ ] Understand role of each file
- [ ] Know where `.env` is located

### Backend Directory
```
backend/.env                  - Synced config with root
backend/database.py           - Database class
backend/parsehub.db          - Database file (actual data)
```

- [ ] Know database file location
- [ ] Know that backend/.env must match root/.env
- [ ] Understand database.py handles all database operations

## ✅ Changing Database Location (If Needed)

If the team needs to move the database:

1. [ ] Edit root `.env`:
   ```
   DATABASE_PATH=/new/path/parsehub.db
   ```

2. [ ] Edit backend `/.env`:
   ```
   DATABASE_PATH=/new/path/parsehub.db
   ```

3. [ ] Move the actual database file to new location

4. [ ] All scripts automatically use new location

5. [ ] No code changes required!

- [ ] Know that this is a simple 3-step process
- [ ] Know that no code modifications are needed

## ✅ Key Principles to Remember

### Unified Database
- [ ] **Only ONE database file is used**: `backend/parsehub.db`
- [ ] **All scripts access same file**: No duplicates, no inconsistency
- [ ] **Configuration is centralized**: Change location in 2 places
- [ ] **Automatic deduplication**: New data replaces old, no manual cleanup

### No Hardcoded Paths
- [ ] **Don't hardcode paths** in scripts
- [ ] **Always use**: `from database_config import DATABASE_PATH`
- [ ] **Benefits**: Works from any directory, on any machine

### Data Consistency
- [ ] **Data is automatically deduplicated**: UNIQUE constraint on unique fields
- [ ] **Update logic**: `INSERT OR REPLACE` handles duplicates
- [ ] **Result**: Inserting same data twice doesn't break anything

## ✅ Important DO's and DON'Ts

### DO:
- ✅ Use `database_config.DATABASE_PATH` when accessing database
- ✅ Check `.env` files when configuration doesn't work
- ✅ Run `verify_unified_database.py` to test the system
- ✅ Update both `.env` files when changing database location
- ✅ Read the documentation when implementing new features

### DON'T:
- ❌ Don't hardcode absolute paths in scripts
- ❌ Don't modify `backend/parsehub.db` directly without backup
- ❌ Don't create separate databases for different scripts
- ❌ Don't manually modify .env files unless following procedures
- ❌ Don't assume database exists in specific location

## ✅ Troubleshooting

### If verification script fails:
1. [ ] Check `.env` file exists: `dir .env`
2. [ ] Check database file exists: `dir backend\parsehub.db`
3. [ ] Verify you're in correct directory
4. [ ] Read troubleshooting section in QUICK_REFERENCE.md

### If script can't find database:
1. [ ] Verify `.env` file has correct DATABASE_PATH
2. [ ] Verify database file exists at that location
3. [ ] Run: `python verify_unified_database.py` to diagnose

### If experiencing errors:
1. [ ] Check error message carefully
2. [ ] Reference QUICK_REFERENCE.md troubleshooting section
3. [ ] Run verification script to check system status

## ✅ What This System Provides

- [x] **Single Source of Truth**: One database file with all data
- [x] **Easy Configuration**: Change location in 2 files
- [x] **Automatic Deduplication**: No duplicate handling code needed
- [x] **Location Independence**: Works from any directory
- [x] **Machine Independence**: No machine-specific paths
- [x] **Cross-Platform**: Works on Windows, Mac, Linux
- [x] **Simple Access**: Import from `database_config`
- [x] **Documented**: Complete guides and references
- [x] **Verified**: Automated verification script
- [x] **Production Ready**: Thoroughly tested

## ✅ Quick Test After Setup

After completing this checklist, run this quick test:

```bash
# 1. Verify system
python verify_unified_database.py

# 2. Check database
python check_database_content.py

# 3. Try simple query
python -c "from database_config import DATABASE_PATH; import sqlite3; db=sqlite3.connect(DATABASE_PATH); print('Products:', db.execute('SELECT COUNT(*) FROM product_data').fetchone()[0])"
```

All three should complete successfully!

## ✅ Questions?

Refer to:
- **How it works?** → `CENTRALIZED_DATABASE.md`
- **Daily tasks?** → `QUICK_REFERENCE.md`
- **Current status?** → `PROJECT_STATUS.md`
- **Getting started?** → `QUICKSTART.md`
- **Project overview?** → `README.md`

## ✅ Completion

- [ ] I understand the unified database system
- [ ] I can access the database from Python scripts
- [ ] I know where the configuration files are
- [ ] I know how to verify the system is working
- [ ] I have read the relevant documentation
- [ ] I can run the common commands
- [ ] I know how to troubleshoot basic issues
- [ ] I'm ready to work with the ParseHub project! 🚀

---

**Welcome to the ParseHub Team!** 🎉

This system was designed to be simple, consistent, and maintainable. If you have questions, refer to the documentation or run the verification script to check system status.

**Key Takeaway**: There is ONE database file (`backend/parsehub.db`) that is used everywhere in the project. Configuration is simple to change, and everything is documented.

Good luck! 💪
