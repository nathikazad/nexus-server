"""
People handler for PKM operations.

This module handles all people-related operations using GraphQL.
"""

import logging
from typing import Dict, Any, List, Optional

from graphql_client import graphql_client

logger = logging.getLogger(__name__)


async def list_people() -> Dict[str, Any]:
    """List all people in the PKM database."""
    try:
        # Use the GetBasicModels query from .gql file
        result = graphql_client.execute_gql_file("GetBasicModels")
        
        if not result["success"]:
            return {
                "people": [],
                "error": result.get("error"),
                "message": "Failed to retrieve people from database.",
                "count": 0
            }
        
        # Filter for Person models and extract data
        models_data = result["data"].get("allModels", {}).get("nodes", [])
        people_list = []
        
        for model in models_data:
            if model["modelTypeByModelTypeId"]["name"] == "Person":
                people_list.append({
                    "id": model["id"],
                    "name": model["title"],
                    "description": model["body"] or "No description available"
                })
        
        return {
            "people": people_list,
            "count": len(people_list),
            "message": f"Found {len(people_list)} people in your knowledge base"
        }
        
    except Exception as e:
        return {
            "people": [],
            "error": str(e),
            "message": "Failed to retrieve people from database.",
            "count": 0
        }


async def add_people(name: str, description: str = "") -> Dict[str, Any]:
    """
    Add a new person to the PKM database.
    
    Args:
        name: The person's name (required)
        description: The person's description (optional)
    
    Returns:
        Dictionary with success status and details about the added person.
    """
    if not name or not name.strip():
        return {
            "success": False,
            "error": "Name is required and cannot be empty",
            "message": "Please provide a valid name for the person"
        }
    
    try:
        # First, get or create the Person model type
        person_type_result = graphql_client.get_model_type_by_name("Person")
        
        if not person_type_result["success"]:
            logger.error(f"Failed to get Person model type: {person_type_result.get('error')}")
            return {
                "success": False,
                "error": "Failed to access Person model type",
                "message": "Could not access Person model type. Please check database connection."
            }
        
        person_type = person_type_result["data"].get("modelTypeByName")
        
        if not person_type:
            # For now, return an error if Person type doesn't exist
            # In a full implementation, you might want to create it via GraphQL mutation
            return {
                "success": False,
                "error": "Person model type not found",
                "message": "Person model type does not exist. Please initialize the database first."
            }
        
        # Check if person with this name already exists
        existing_people_result = graphql_client.get_models_by_type("Person")
        
        if existing_people_result["success"]:
            existing_models = existing_people_result["data"].get("allModels", {}).get("nodes", [])
            for model in existing_models:
                if model["title"] == name.strip():
                    return {
                        "success": False,
                        "error": "Person already exists",
                        "message": f"A person named '{name}' already exists in your knowledge base",
                        "existing_person": {
                            "id": model["id"],
                            "name": model["title"],
                            "description": model["body"] or "No description"
                        }
                    }
        
        # Create new person
        create_result = graphql_client.create_model(
            model_type_id=person_type["id"],
            title=name.strip(),
            body=description.strip() if description else None
        )
        
        if not create_result["success"]:
            logger.error(f"Failed to create person: {create_result.get('error')}")
            return {
                "success": False,
                "error": "Failed to create person",
                "message": f"Could not add '{name}' to database. Please check database connection."
            }
        
        new_person_data = create_result["data"]["createModel"]["model"]
        
        logger.info(f"Added new person: {name}")
        
        return {
            "success": True,
            "person": {
                "id": str(new_person_data["id"]),
                "name": new_person_data["title"],
                "description": new_person_data["body"] or "No description"
            },
            "message": f"Successfully added '{name}' to your knowledge base"
        }
        
    except Exception as e:
        logger.error(f"Error adding person: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add person to database. Please check database connection."
        }


async def get_person_details(person_id: int) -> Dict[str, Any]:
    """Get comprehensive details for a specific person by their ID."""
    try:
        # Use the GetModelById query from .gql file
        result = graphql_client.execute_gql_file("GetModelById", {"modelId": person_id})
        
        if not result["success"]:
            return {
                "success": False,
                "error": result.get("error"),
                "message": f"Could not retrieve data for person ID {person_id}.",
                "person_id": person_id
            }
        
        model_data = result["data"].get("modelById")
        
        if not model_data:
            return {
                "success": False,
                "error": "Person not found",
                "message": f"No person found with ID {person_id}",
                "person_id": person_id
            }
        
        # Return the data directly from GraphQL
        return {
            "success": True,
            "person_id": person_id,
            "data": model_data,
            "message": f"Successfully retrieved details for person {person_id}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to retrieve person details for ID {person_id}.",
            "person_id": person_id
        }
