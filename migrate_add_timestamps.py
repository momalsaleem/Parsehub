"""
Database migration: Add created_at and updated_at columns to projects table
"""
import sqlite3
import sys
from pathlib import Path


def migrate_database(db_path: str):
    """Add timestamp columns to projects and runs tables if they don't exist"""
    print(f"Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check projects table
        print("\n--- Projects Table ---")
        cursor.execute("PRAGMA table_info(projects)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {columns}")

        # Add created_at to projects if it doesn't exist
        if 'created_at' not in columns:
            print("Adding created_at column to projects...")
            cursor.execute('''
                ALTER TABLE projects 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''')
            print("✓ created_at column added to projects")
        else:
            print("✓ created_at column already exists in projects")

        # Add updated_at to projects if it doesn't exist
        if 'updated_at' not in columns:
            print("Adding updated_at column to projects...")
            cursor.execute('''
                ALTER TABLE projects 
                ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ''')
            print("✓ updated_at column added to projects")
        else:
            print("✓ updated_at column already exists in projects")

        # Check runs table
        print("\n--- Runs Table ---")
        cursor.execute("PRAGMA table_info(runs)")
        runs_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {runs_columns}")

        # Add updated_at to runs if it doesn't exist
        if 'updated_at' not in runs_columns:
            print("Adding updated_at column to runs...")
            # SQLite doesn't allow CURRENT_TIMESTAMP as default in ALTER TABLE
            # So we add it with NULL default, then update existing rows
            cursor.execute('''
                ALTER TABLE runs 
                ADD COLUMN updated_at TIMESTAMP DEFAULT NULL
            ''')
            # Update existing rows to have a timestamp
            cursor.execute('''
                UPDATE runs 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE updated_at IS NULL
            ''')
            print("✓ updated_at column added to runs")
        else:
            print("✓ updated_at column already exists in runs")

        conn.commit()
        conn.close()

        print(f"\n✅ Migration completed successfully for {db_path}")
        return True

    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Migrate both database files
    root_db = Path(__file__).parent / "parsehub.db"
    backend_db = Path(__file__).parent / "backend" / "parsehub.db"

    success = True

    if root_db.exists():
        print("=" * 80)
        success = migrate_database(str(root_db)) and success
    else:
        print(f"Database not found: {root_db}")

    if backend_db.exists():
        print("=" * 80)
        success = migrate_database(str(backend_db)) and success
    else:
        print(f"Database not found: {backend_db}")

    if success:
        print("\n" + "=" * 80)
        print("🎉 All migrations completed successfully!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("⚠️  Some migrations failed. Please check the errors above.")
        print("=" * 80)
        sys.exit(1)
