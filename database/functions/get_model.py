#!/usr/bin/env python3
"""
Helper script to run the get_model_full PostgreSQL function
"""

import sys
import json
import os
# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import SessionLocal
from sqlalchemy import text
from type_utils import standardize_model_full_data_response, validate_and_log_response

def get_model_full(model_id):
    """
    Call the get_model_full PostgreSQL function for a given model ID
    
    Args:
        model_id (int): The ID of the model to retrieve
        
    Returns:
        dict: The standardized full model data structure
    """
    db = SessionLocal()
    try:
        result = db.execute(text('SELECT get_model_full(:model_id)'), {'model_id': model_id})
        function_result = result.fetchone()[0]
        
        if function_result:
            # Standardize the response structure
            standardized_result = standardize_model_full_data_response(function_result)
            # Validate the structure
            validate_and_log_response(standardized_result, "model_full_data")
            return standardized_result
        else:
            return None
            
    except Exception as e:
        print(f"Error calling function: {e}")
        return None
    finally:
        db.close()

def list_models():
    """List all available models in the database"""
    db = SessionLocal()
    try:
        result = db.execute(text('SELECT id, title FROM models ORDER BY id'))
        models = result.fetchall()
        return models
    except Exception as e:
        print(f"Error listing models: {e}")
        return []
    finally:
        db.close()

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python get_model.py <model_id>     # Get full data for specific model")
        print("  python get_model.py list           # List all available models")
        print("  python get_model.py all            # Get full data for all models")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        print("Available models:")
        models = list_models()
        for model in models:
            print(f"  ID: {model[0]}, Title: {model[1]}")
    
    elif command == "all":
        print("Getting full data for all models:")
        models = list_models()
        for model in models:
            print(f"\n=== Model {model[0]}: {model[1]} ===")
            result = get_model_full(model[0])
            if result:
                print(json.dumps(result, indent=2, default=str))
    
    else:
        try:
            model_id = int(command)
            print(f"Getting full data for model {model_id}:")
            result = get_model_full(model_id)
            if result:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("No data found or error occurred")
        except ValueError:
            print("Error: Model ID must be a number")
            print("Use 'list' to see available models")

if __name__ == "__main__":
    main()
