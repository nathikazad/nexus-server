"""
Database models package.

This package contains SQLAlchemy model definitions for the GraphQL API.
PostGraphile automatically generates GraphQL schema from these models.
"""

from .models import (
    Base, ModelType, Model, TraitAssignment, AttributeDefinition, 
    Attribute, RelationshipType, RelationAttributeDefinition, 
    Relation, RelationAttribute, Embedding, SessionLocal, engine, get_db, create_tables
)

__all__ = [
    # SQLAlchemy models - these are used by PostGraphile to generate GraphQL schema
    'Base', 'ModelType', 'Model', 'TraitAssignment', 'AttributeDefinition',
    'Attribute', 'RelationshipType', 'RelationAttributeDefinition',
    'Relation', 'RelationAttribute', 'Embedding', 'SessionLocal', 'engine', 'get_db', 'create_tables'
]
