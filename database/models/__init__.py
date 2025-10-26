"""
Database models package.

This package contains all database model definitions, type definitions,
and utility functions for data validation and standardization.
"""

from .models import (
    Base, ModelType, Model, TraitAssignment, AttributeDefinition, 
    Attribute, RelationshipType, RelationAttributeDefinition, 
    Relation, RelationAttribute, Embedding, SessionLocal, engine, get_db, create_tables
)
from .model_types import (
    BaseModelType, TraitType, ModelType as ModelTypeClass,
    Model as ModelClass, RelationAttribute as RelationAttributeClass,
    Relation as RelationClass, ModelFullData,
    validate_model_type_structure, validate_model_structure, 
    validate_model_full_data_structure,
    EXAMPLE_MODEL_TYPE, EXAMPLE_MODEL, EXAMPLE_MODEL_FULL_DATA
)
from .type_utils import (
    standardize_model_type_response, standardize_model_response,
    standardize_model_full_data_response, validate_and_log_response,
    ensure_consistent_response, create_standardized_success_response,
    create_standardized_error_response
)

__all__ = [
    # SQLAlchemy models
    'Base', 'ModelType', 'Model', 'TraitAssignment', 'AttributeDefinition',
    'Attribute', 'RelationshipType', 'RelationAttributeDefinition',
    'Relation', 'RelationAttribute', 'Embedding', 'SessionLocal', 'engine', 'get_db', 'create_tables',
    
    # Type definitions
    'BaseModelType', 'TraitType', 'ModelTypeClass', 'ModelClass', 
    'RelationAttributeClass', 'RelationClass', 'ModelFullData',
    
    # Validation functions
    'validate_model_type_structure', 'validate_model_structure', 
    'validate_model_full_data_structure',
    
    # Utility functions
    'standardize_model_type_response', 'standardize_model_response',
    'standardize_model_full_data_response', 'validate_and_log_response',
    'ensure_consistent_response', 'create_standardized_success_response',
    'create_standardized_error_response',
    
    # Examples
    'EXAMPLE_MODEL_TYPE', 'EXAMPLE_MODEL', 'EXAMPLE_MODEL_FULL_DATA'
]
