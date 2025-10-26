"""
Type definitions for consistent database function return values.

This module defines the static types for all database functions to ensure
consistent return structures across the application.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass


@dataclass
class BaseModelType:
    """Base model type information."""
    id: int
    name: str
    description: Optional[str]


@dataclass
class TraitType:
    """Trait type information."""
    id: int
    name: str
    description: Optional[str]


@dataclass
class ModelType:
    """Complete model type structure with base model and traits."""
    base_model: BaseModelType
    traits: List[TraitType]


@dataclass
class Model:
    """Basic model information."""
    id: int
    title: str
    body: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class RelationAttribute:
    """Relation attribute information."""
    key: str
    value: Union[str, int, bool, datetime, None]


@dataclass
class Relation:
    """Relation information."""
    relation_id: int
    relation_name: str
    direction: str  # 'incoming' or 'outgoing'
    other_model: Model
    relation_attributes: Optional[Dict[str, Any]]


@dataclass
class ModelFullData:
    """Complete model data structure returned by get_model_full function."""
    model: Model
    model_type: ModelType
    attributes: Dict[str, Any]
    relations: List[Relation]


# Type aliases for common return structures
ModelTypeDict = Dict[str, Any]
ModelDict = Dict[str, Any]
TraitDict = Dict[str, Any]
RelationDict = Dict[str, Any]
ModelFullDataDict = Dict[str, Any]

# Function return type definitions
def validate_model_type_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that a model_type structure follows the expected format.
    
    Expected structure:
    {
        "base_model": {"id": int, "name": str, "description": str},
        "traits": [{"id": int, "name": str, "description": str}]
    }
    """
    if not isinstance(data, dict):
        return False
    
    # Check for base_model
    if "base_model" not in data:
        return False
    
    base_model = data["base_model"]
    if not isinstance(base_model, dict):
        return False
    
    required_base_fields = ["id", "name", "description"]
    if not all(field in base_model for field in required_base_fields):
        return False
    
    # Check for traits
    if "traits" not in data:
        return False
    
    traits = data["traits"]
    if not isinstance(traits, list):
        return False
    
    # Validate each trait
    for trait in traits:
        if not isinstance(trait, dict):
            return False
        required_trait_fields = ["id", "name", "description"]
        if not all(field in trait for field in required_trait_fields):
            return False
    
    return True


def validate_model_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that a model structure follows the expected format.
    
    Expected structure:
    {
        "id": int,
        "title": str,
        "body": str,
        "created_at": datetime,
        "updated_at": datetime
    }
    """
    if not isinstance(data, dict):
        return False
    
    required_fields = ["id", "title", "body", "created_at", "updated_at"]
    return all(field in data for field in required_fields)


def validate_model_full_data_structure(data: Dict[str, Any]) -> bool:
    """
    Validate that a complete model data structure follows the expected format.
    
    Expected structure:
    {
        "model": ModelDict,
        "model_type": ModelTypeDict,
        "attributes": Dict[str, Any],
        "relations": List[RelationDict]
    }
    """
    if not isinstance(data, dict):
        return False
    
    required_fields = ["model", "model_type", "attributes", "relations"]
    if not all(field in data for field in required_fields):
        return False
    
    # Validate model structure
    if not validate_model_structure(data["model"]):
        return False
    
    # Validate model_type structure
    if not validate_model_type_structure(data["model_type"]):
        return False
    
    # Validate relations
    relations = data["relations"]
    if not isinstance(relations, list):
        return False
    
    return True


# Example usage and documentation
EXAMPLE_MODEL_TYPE = {
    "base_model": {
        "id": 1,
        "name": "Person",
        "description": "A human person"
    },
    "traits": [
        {
            "id": 3,
            "name": "Employee",
            "description": "Someone who works for a company"
        }
    ]
}

EXAMPLE_MODEL = {
    "id": 1,
    "title": "Alice Johnson",
    "body": "Software engineer with 5 years experience",
    "created_at": "2025-10-25T21:30:25.669066",
    "updated_at": "2025-10-25T21:30:25.669069"
}

EXAMPLE_MODEL_FULL_DATA = {
    "model": EXAMPLE_MODEL,
    "model_type": EXAMPLE_MODEL_TYPE,
    "attributes": {"age": "28"},
    "relations": [
        {
            "relation_id": 1,
            "relation_name": "works_for",
            "direction": "outgoing",
            "other_model": {
                "id": 3,
                "title": "Acme Corporation",
                "body": "Leading technology company",
                "created_at": "2025-10-25T21:30:25.669071",
                "updated_at": "2025-10-25T21:30:25.669072"
            },
            "relation_attributes": None
        }
    ]
}
