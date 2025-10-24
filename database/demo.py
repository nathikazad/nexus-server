#!/usr/bin/env python3
"""
Demo script showing SQLAlchemy + Alembic migrations with PostgreSQL

This script demonstrates:
1. Running migrations to create tables
2. Adding data to the database
3. Querying the database
4. Running a migration to add a column
5. Updating data with the new column

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

from models import User, SessionLocal, engine
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

def demo_database_operations():
    """Demonstrate database operations"""
    print("\n📊 Demonstrating database operations...")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Add some sample users
        print("\n➕ Adding sample users...")
        
        users_data = [
            {"name": "Alice Johnson", "email": "alice@example.com", "age": 28},
            {"name": "Bob Smith", "email": "bob@example.com", "age": 32},
            {"name": "Charlie Brown", "email": "charlie@example.com", "age": 25},
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print("✅ Users added successfully!")
        
        # Query users
        print("\n🔍 Querying users...")
        users = db.query(User).all()
        
        for user in users:
            print(f"  - {user}")
        
        # Update a user
        print("\n✏️  Updating user...")
        alice = db.query(User).filter(User.email == "alice@example.com").first()
        if alice:
            alice.age = 29
            db.commit()
            print(f"✅ Updated Alice's age: {alice}")
        
        # Query with filter
        print("\n🔍 Querying users over 30...")
        older_users = db.query(User).filter(User.age > 30).all()
        for user in older_users:
            print(f"  - {user}")
            
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        db.rollback()
    finally:
        db.close()

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

def main():
    """Main demo function"""
    print("🚀 SQLAlchemy + Alembic + PostgreSQL Demo")
    print("=" * 50)
    
    # Setup database
    if not setup_database():
        return
    
    # Run migrations
    if not run_migrations():
        return
    
    # Show migration history
    show_migration_history()
    
    # Demo database operations
    demo_database_operations()
    
    print("\n🎉 Demo completed successfully!")
    print("\n📋 What we demonstrated:")
    print("1. ✅ Database connection and setup")
    print("2. ✅ Running Alembic migrations")
    print("3. ✅ Creating tables (users table)")
    print("4. ✅ Adding a new column (age column)")
    print("5. ✅ CRUD operations with SQLAlchemy")
    print("6. ✅ Querying and filtering data")

if __name__ == "__main__":
    main()
