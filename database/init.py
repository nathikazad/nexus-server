#!/usr/bin/env python3
"""
Database initialization script for SQLAlchemy + Alembic + PostgreSQL Graph Document Schema

This script handles:
1. Database connection setup and testing
2. Running Alembic migrations
3. Showing migration history

Prerequisites:
- PostgreSQL running locally (or configure remote connection)
- Database 'nexus_db' created
- Environment variables configured (see env_example.txt)
"""

import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import SessionLocal, engine
from config import db_config

def setup_database():
    """Create the database if it doesn't exist"""
    print("🔧 Setting up database...")
    print(f"Database URL: {db_config.database_url}")
    
    # Test connection
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n📋 Setup instructions:")
        print("1. Install PostgreSQL locally:")
        print("   brew install postgresql")
        print("   brew services start postgresql")
        print("\n2. Create database:")
        print("   createdb nexus_db")
        print("\n3. Copy env_example.txt to .env and update with your credentials")
        return False
    
    return True

def run_migrations():
    """Run Alembic migrations"""
    print("\n🔄 Running migrations...")
    
    # Import alembic command
    from alembic.config import Config
    from alembic import command
    
    # Set up alembic config
    alembic_cfg = Config("alembic.ini")
    
    try:
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def show_migration_history():
    """Show migration history"""
    print("\n📜 Migration history:")
    
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    
    try:
        command.history(alembic_cfg)
    except Exception as e:
        print(f"❌ Failed to show history: {e}")

def initialize_database():
    """Initialize the database with migrations"""
    print("🚀 Initializing Database")
    print("=" * 40)
    
    # Setup database
    if not setup_database():
        return False
    
    # Run migrations
    if not run_migrations():
        return False
    
    # Show migration history
    show_migration_history()
    
    print("\n✅ Database initialization completed successfully!")
    return True

if __name__ == "__main__":
    initialize_database()
