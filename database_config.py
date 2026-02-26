"""
Centralized Database Configuration
All files in this project should use this configuration for database access
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "backend" / ".env")
load_dotenv(Path(__file__).parent / ".env")

# Get database path from environment or use default
DATABASE_PATH = os.getenv(
    'DATABASE_PATH',
    str(Path(__file__).parent / "backend" / "parsehub.db")
)

# Ensure it's an absolute path
if not os.path.isabs(DATABASE_PATH):
    DATABASE_PATH = str(Path(__file__).parent / DATABASE_PATH)

print(f"Database configured: {DATABASE_PATH}")
