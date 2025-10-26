#!/usr/bin/env python3
"""
Complete Database Reset Script

This script provides multiple ways to reset the database:
1. Recreate database (empty) - default
2. Recreate database and run migrations
3. Recreate database, run migrations, and load sample data

All options completely drop and recreate the entire database.

Usage:
    python reset_db.py                    # Recreate database (empty)
    python reset_db.py --with-migrations  # Recreate database and run migrations
    python reset_db.py --with-data        # Recreate database, run migrations, and load data
    python reset_db.py --help             # Show help
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import db_config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def print_banner():
    """Print a nice banner"""
    print("=" * 60)
    print("🗑️  DATABASE RESET UTILITY")
    print("=" * 60)
    print(f"Database: {db_config.database}")
    print(f"Host: {db_config.host}:{db_config.port}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(db_config.database_url)
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def drop_all_tables():
    """Drop all tables in the correct order"""
    print("\n🗑️  Dropping all tables...")
    
    conn = psycopg2.connect(db_config.database_url)
    cur = conn.cursor()
    
    try:
        # Drop all tables in correct order (respecting foreign key constraints)
        tables = [
            'relation_attributes', 'trait_assignments', 'relations', 
            'relation_attribute_definitions', 'embeddings', 'attributes',
            'relationship_type', 'models', 'attribute_definitions', 'model_types'
        ]
        
        for table in tables:
            cur.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
            print(f"  ✓ Dropped table: {table}")
        
        conn.commit()
        print("✅ All tables dropped successfully!")
        
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def drop_alembic_version():
    """Drop alembic version tracking table"""
    print("\n🗑️  Dropping alembic version table...")
    
    conn = psycopg2.connect(db_config.database_url)
    cur = conn.cursor()
    
    try:
        cur.execute('DROP TABLE IF EXISTS alembic_version;')
        conn.commit()
        print("✅ Alembic version table dropped!")
    except Exception as e:
        print(f"❌ Error dropping alembic version: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def recreate_database():
    """Completely recreate the database"""
    print("\n🗑️  Recreating entire database...")
    
    # Connect to postgres database to drop/create our database
    postgres_url = f'postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/postgres'
    
    conn = psycopg2.connect(postgres_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    try:
        # Terminate any existing connections to our database
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_config.database}' AND pid <> pg_backend_pid();
        """)
        
        # Drop and recreate database
        cur.execute(f'DROP DATABASE IF EXISTS {db_config.database};')
        print(f"  ✓ Dropped database: {db_config.database}")
        
        cur.execute(f'CREATE DATABASE {db_config.database};')
        print(f"  ✓ Created database: {db_config.database}")
        
        print("✅ Database recreated successfully!")
        
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def run_migrations():
    """Run alembic migrations"""
    print("\n🔄 Running migrations...")
    
    try:
        # Run alembic upgrade
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migrations applied successfully!")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False
    
    return True

def load_sample_data():
    """Load sample data using load_data.py"""
    print("\n📊 Loading sample data...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'admin_functions/load_data.py'],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Sample data loaded successfully!")
            if result.stdout:
                print(f"Output: {result.stdout.strip()}")
        else:
            print(f"❌ Sample data loading failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False
    
    return True

def verify_database():
    """Verify database structure"""
    print("\n🔍 Verifying database structure...")
    
    conn = psycopg2.connect(db_config.database_url)
    cur = conn.cursor()
    
    try:
        # Check if tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        
        expected_tables = [
            'model_types', 'models', 'trait_assignments', 'attribute_definitions',
            'attributes', 'relationship_type', 'relation_attribute_definitions',
            'relations', 'relation_attributes', 'embeddings', 'alembic_version'
        ]
        
        print(f"Found {len(tables)} tables:")
        for table in tables:
            status = "✅" if table in expected_tables else "⚠️"
            print(f"  {status} {table}")
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
        
        # Check alembic version
        cur.execute("SELECT version_num FROM alembic_version;")
        version = cur.fetchone()
        if version:
            print(f"✅ Alembic version: {version[0]}")
        else:
            print("⚠️  No alembic version found")
        
        print("✅ Database verification completed!")
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
    finally:
        cur.close()
        conn.close()

def complete_reset(with_data=False):
    """Perform complete database reset"""
    print_banner()
    
    try:
        # Step 1: Recreate entire database
        recreate_database()
        
        # Step 2: Run migrations
        if not run_migrations():
            return False
        
        # Step 3: Load sample data if requested
        if with_data:
            if not load_sample_data():
                return False
        
        # Step 4: Verify everything
        verify_database()
        
        print("\n🎉 Database reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database reset failed: {e}")
        return False


def drop_tables_only():
    """Drop entire database (no migrations, no data)"""
    print_banner()
    
    try:
        # Step 1: Recreate entire database
        recreate_database()
        
        # Step 2: Verify database is empty
        print("\n🔍 Verifying database is empty...")
        conn = psycopg2.connect(db_config.database_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        remaining_tables = [row[0] for row in cur.fetchall()]
        if remaining_tables:
            print(f"⚠️  Remaining tables: {', '.join(remaining_tables)}")
        else:
            print("✅ Database is completely empty!")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Database recreated successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database recreation failed: {e}")
        return False

def tables_with_migrations_reset():
    """Reset database and run migrations"""
    print_banner()
    
    try:
        # Step 1: Recreate entire database
        recreate_database()
        
        # Step 2: Run migrations
        if not run_migrations():
            return False
        
        # Step 3: Verify everything
        verify_database()
        
        print("\n🎉 Database reset with migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database reset with migrations failed: {e}")
        return False

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Complete Database Reset Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reset_db.py                    # Recreate database (empty)
  python reset_db.py --with-migrations  # Recreate database and run migrations
  python reset_db.py --with-data        # Recreate database, run migrations, and load data
  python reset_db.py --verify           # Just verify database structure
        """
    )
    
    parser.add_argument(
        '--with-migrations', 
        action='store_true',
        help='Recreate database and run migrations'
    )
    
    parser.add_argument(
        '--with-data', 
        action='store_true',
        help='Recreate database, run migrations, and load sample data'
    )
    
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Just verify database structure'
    )
    
    args = parser.parse_args()
    
    if args.verify:
        print_banner()
        if test_connection():
            verify_database()
        return
    
    if args.with_data:
        success = complete_reset(with_data=True)
    elif args.with_migrations:
        success = tables_with_migrations_reset()
    else:
        # Default: recreate database (empty)
        success = drop_tables_only()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
