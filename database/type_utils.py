"""
Utility functions for ensuring consistent return types across database functions.

This module provides helper functions to standardize return values and validate
data structures according to the defined types.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from model_types import (
    validate_model_type_structure,
    validate_model_structure,
    validate_model_full_data_structure
)

logger = logging.getLogger(__name__)


def standardize_model_type_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize a model_type response to ensure it follows the expected structure.
    
    Args:
        data: Raw data from database function
        
    Returns:
        Standardized model_type structure
    """
    if not isinstance(data, dict):
        logger.warning("Invalid model_type data: not a dictionary")
        return {"base_model": {"id": 0, "name": "Unknown", "description": None}, "traits": []}
    
    # Ensure base_model structure
    base_model = data.get("base_model", {})
    if not isinstance(base_model, dict):
        base_model = {}
    
    standardized_base_model = {
        "id": base_model.get("id", 0),
        "name": base_model.get("name", "Unknown"),
        "description": base_model.get("description")
    }
    
    # Ensure traits structure
    traits = data.get("traits", [])
    if not isinstance(traits, list):
        traits = []
    
    standardized_traits = []
    for trait in traits:
        if isinstance(trait, dict):
            standardized_trait = {
                "id": trait.get("id", 0),
                "name": trait.get("name", "Unknown"),
                "description": trait.get("description")
            }
            standardized_traits.append(standardized_trait)
    
    return {
        "base_model": standardized_base_model,
        "traits": standardized_traits
    }


def standardize_model_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize a model response to ensure it follows the expected structure.
    
    Args:
        data: Raw data from database function
        
    Returns:
        Standardized model structure with model_type included
    """
    if not isinstance(data, dict):
        logger.warning("Invalid model data: not a dictionary")
        return {
            "id": 0,
            "title": "Unknown",
            "body": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "model_type": standardize_model_type_response({})
        }
    
    return {
        "id": data.get("id", 0),
        "title": data.get("title", "Unknown"),
        "body": data.get("body"),
        "created_at": data.get("created_at", datetime.utcnow()),
        "updated_at": data.get("updated_at", datetime.utcnow()),
        "model_type": standardize_model_type_response(data.get("model_type", {}))
    }


def standardize_model_full_data_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Standardize a complete model data response to ensure it follows the expected structure.
    
    Args:
        data: Raw data from database function
        
    Returns:
        Standardized model full data structure
    """
    if not isinstance(data, dict):
        logger.warning("Invalid model full data: not a dictionary")
        return {
            "model": standardize_model_response({}),
            "attributes": {},
            "relations": []
        }
    
    return {
        "model": standardize_model_response(data.get("model", {})),
        "attributes": data.get("attributes", {}),
        "relations": data.get("relations", [])
    }


def validate_and_log_response(data: Dict[str, Any], data_type: str) -> bool:
    """
    Validate a response structure and log any issues.
    
    Args:
        data: Data to validate
        data_type: Type of data being validated ("model", "model_type", "model_full_data")
        
    Returns:
        True if valid, False otherwise
    """
    is_valid = False
    
    if data_type == "model":
        is_valid = validate_model_structure(data)
    elif data_type == "model_type":
        is_valid = validate_model_type_structure(data)
    elif data_type == "model_full_data":
        is_valid = validate_model_full_data_structure(data)
    else:
        logger.warning(f"Unknown data type for validation: {data_type}")
        return False
    
    if not is_valid:
        logger.warning(f"Invalid {data_type} structure: {data}")
    else:
        logger.debug(f"Valid {data_type} structure")
    
    return is_valid


def ensure_consistent_response(func):
    """
    Decorator to ensure consistent response structure from database functions.
    
    This decorator can be applied to functions that return model data to ensure
    they follow the standardized structure.
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If result is a dictionary, standardize it
            if isinstance(result, dict):
                if "model" in result and "model_type" in result:
                    # This looks like model_full_data
                    result = standardize_model_full_data_response(result)
                    validate_and_log_response(result, "model_full_data")
                elif "base_model" in result and "traits" in result:
                    # This looks like model_type
                    result = standardize_model_type_response(result)
                    validate_and_log_response(result, "model_type")
                elif "id" in result and "title" in result:
                    # This looks like a model
                    result = standardize_model_response(result)
                    validate_and_log_response(result, "model")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            # Return a safe default structure
            if "model" in str(func.__name__):
                return standardize_model_response({})
            return {}
    
    return wrapper


# Example usage for existing functions
def create_standardized_success_response(data: Dict[str, Any], message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response for API endpoints.
    
    Args:
        data: The data to return
        message: Success message
        
    Returns:
        Standardized response structure
    """
    return {
        "success": True,
        "data": data,
        "message": message
    }


def create_standardized_error_response(error: str, message: str = "Error occurred") -> Dict[str, Any]:
    """
    Create a standardized error response for API endpoints.
    
    Args:
        error: Error details
        message: Error message
        
    Returns:
        Standardized error response structure
    """
    return {
        "success": False,
        "error": error,
        "message": message
    }
