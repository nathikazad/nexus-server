#!/usr/bin/env python3
"""
Demo script showing SQLAlchemy + Alembic migrations with PostgreSQL Graph Document Schema

This script demonstrates:
1. Running migrations to create the graph document schema
2. Creating model types, models, and relationships
3. EAV (Entity-Attribute-Value) system
4. Trait assignments and graph traversal
5. Complex queries across the graph

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

from models import (
    ModelType, Model, TraitAssignment, AttributeDefinition, Attribute,
    RelationshipType, Relation, SessionLocal, engine
)
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
    """Demonstrate database operations with graph document schema"""
    print("\n📊 Demonstrating graph document operations...")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Create model types
        print("\n➕ Creating model types...")
        
        # Create base types
        person_type = ModelType(
            name="Person",
            type_kind="base",
            description="A human person"
        )
        company_type = ModelType(
            name="Company", 
            type_kind="base",
            description="A business organization"
        )
        
        # Create trait types
        employee_trait = ModelType(
            name="Employee",
            type_kind="trait",
            description="Someone who works for a company"
        )
        
        db.add_all([person_type, company_type, employee_trait])
        db.commit()
        print("✅ Model types created successfully!")
        
        # Create models (documents)
        print("\n➕ Creating models...")
        
        alice = Model(
            model_type_id=person_type.id,
            title="Alice Johnson",
            body="Software engineer with 5 years experience"
        )
        
        bob = Model(
            model_type_id=person_type.id,
            title="Bob Smith", 
            body="Product manager with 8 years experience"
        )
        
        acme_corp = Model(
            model_type_id=company_type.id,
            title="Acme Corporation",
            body="Leading technology company"
        )
        
        db.add_all([alice, bob, acme_corp])
        db.commit()
        print("✅ Models created successfully!")
        
        # Create attribute definitions
        print("\n➕ Creating attribute definitions...")
        
        age_attr = AttributeDefinition(
            model_type_id=person_type.id,
            key="age",
            value_type="number",
            required=True
        )
        
        salary_attr = AttributeDefinition(
            model_type_id=employee_trait.id,
            key="salary",
            value_type="number",
            required=False
        )
        
        db.add_all([age_attr, salary_attr])
        db.commit()
        print("✅ Attribute definitions created successfully!")
        
        # Create attributes (EAV values)
        print("\n➕ Creating attributes...")
        
        alice_age = Attribute(
            model_id=alice.id,
            attribute_definition_id=age_attr.id,
            value_number=28
        )
        
        bob_age = Attribute(
            model_id=bob.id,
            attribute_definition_id=age_attr.id,
            value_number=32
        )
        
        db.add_all([alice_age, bob_age])
        db.commit()
        print("✅ Attributes created successfully!")
        
        # Create trait assignments
        print("\n➕ Creating trait assignments...")
        
        alice_employee = TraitAssignment(
            model_id=alice.id,
            trait_type_id=employee_trait.id
        )
        
        bob_employee = TraitAssignment(
            model_id=bob.id,
            trait_type_id=employee_trait.id
        )
        
        db.add_all([alice_employee, bob_employee])
        db.commit()
        print("✅ Trait assignments created successfully!")
        
        # Create relationship type
        print("\n➕ Creating relationship type...")
        
        works_for_rel = RelationshipType(
            from_model_type_id=person_type.id,
            to_model_type_id=company_type.id,
            relation_name="works_for",
            multiplicity="many"
        )
        
        db.add(works_for_rel)
        db.commit()
        print("✅ Relationship type created successfully!")
        
        # Create relations
        print("\n➕ Creating relations...")
        
        alice_works_for_acme = Relation(
            from_id=alice.id,
            to_id=acme_corp.id,
            relationship_type_id=works_for_rel.id
        )
        
        bob_works_for_acme = Relation(
            from_id=bob.id,
            to_id=acme_corp.id,
            relationship_type_id=works_for_rel.id
        )
        
        db.add_all([alice_works_for_acme, bob_works_for_acme])
        db.commit()
        print("✅ Relations created successfully!")
        
        # Query and display results
        print("\n🔍 Querying models...")
        models = db.query(Model).all()
        for model in models:
            print(f"  - {model}")
        
        # Alternative simpler query for ages
        print("\n🔍 All people with their ages...")
        age_attrs = db.query(Attribute).join(AttributeDefinition).filter(
            AttributeDefinition.key == "age"
        ).all()
        for attr in age_attrs:
            person = db.query(Model).filter(Model.id == attr.model_id).first()
            if person:
                print(f"  - {person.title} (age: {attr.value_number})")
        
        print("\n🔍 Querying employees...")
        employees = db.query(Model).join(TraitAssignment).join(ModelType).filter(
            ModelType.name == "Employee"
        ).all()
        for employee in employees:
            print(f"  - {employee.title} (Employee)")
            
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
    print("🚀 SQLAlchemy + Alembic + PostgreSQL Graph Document Demo")
    print("=" * 60)
    
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
    print("3. ✅ Graph document schema operations")
    print("4. ✅ Creating model types and models")
    print("5. ✅ EAV (Entity-Attribute-Value) system")
    print("6. ✅ Trait assignments and relationships")
    print("7. ✅ Graph traversal and queries")

if __name__ == "__main__":
    main()
