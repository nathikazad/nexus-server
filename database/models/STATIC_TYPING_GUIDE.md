# Static Typing Guide for Database Functions

This guide explains how to enforce consistent, statically typed return values for all database functions that return `model_type` or related data structures.

## Overview

We've implemented a comprehensive type system to ensure all database functions return consistent, well-defined data structures. This prevents type inconsistencies and makes the API more predictable and maintainable.

## Type Definitions

### Core Types

All type definitions are in `model_types.py`:

```python
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
```

### Standardized Return Structures

#### Model Type Structure
```json
{
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
```

#### Model Structure
```json
{
  "id": 1,
  "title": "Alice Johnson",
  "body": "Software engineer with 5 years experience",
  "created_at": "2025-10-25T21:30:25.669066",
  "updated_at": "2025-10-25T21:30:25.669069"
}
```

## How to Enforce Consistent Types

### 1. Use Type Utilities

Import and use the type utilities in your functions:

```python
from type_utils import (
    standardize_model_type_response,
    standardize_model_response,
    standardize_model_full_data_response,
    validate_and_log_response
)
```

### 2. Apply Standardization

Wrap your database function results with standardization:

```python
def get_model_type_data(model_id: int) -> Dict[str, Any]:
    """Get model type data with consistent structure."""
    db = SessionLocal()
    try:
        # Your database query here
        raw_result = db.execute(text('SELECT ...'), {'model_id': model_id})
        raw_data = raw_result.fetchone()[0]
        
        # Standardize the response
        standardized_result = standardize_model_type_response(raw_data)
        
        # Validate the structure
        validate_and_log_response(standardized_result, "model_type")
        
        return standardized_result
    finally:
        db.close()
```

### 3. Use the Decorator Pattern

For functions that return model data, use the decorator:

```python
from type_utils import ensure_consistent_response

@ensure_consistent_response
def get_model_data(model_id: int) -> Dict[str, Any]:
    """This function will automatically have its response standardized."""
    # Your function implementation
    return raw_data
```

### 4. Create Standardized API Responses

Use the helper functions for API endpoints:

```python
from type_utils import (
    create_standardized_success_response,
    create_standardized_error_response
)

async def get_person_details(person_id: int) -> Dict[str, Any]:
    """Get person details with standardized response."""
    try:
        data = get_model_full(person_id)
        if data:
            return create_standardized_success_response(
                data, 
                f"Successfully retrieved person {person_id}"
            )
        else:
            return create_standardized_error_response(
                "Person not found",
                f"No person found with ID {person_id}"
            )
    except Exception as e:
        return create_standardized_error_response(
            str(e),
            "Failed to retrieve person details"
        )
```

## Validation Functions

### Built-in Validators

Use these functions to validate your data structures:

```python
from model_types import (
    validate_model_type_structure,
    validate_model_structure,
    validate_model_full_data_structure
)

# Validate model type
is_valid = validate_model_type_structure(data)

# Validate model
is_valid = validate_model_structure(data)

# Validate complete model data
is_valid = validate_model_full_data_structure(data)
```

### Custom Validation

You can create custom validators for specific use cases:

```python
def validate_custom_structure(data: Dict[str, Any]) -> bool:
    """Validate a custom data structure."""
    required_fields = ["field1", "field2", "field3"]
    return all(field in data for field in required_fields)
```

## Best Practices

### 1. Always Standardize Database Results

Never return raw database results directly. Always pass them through standardization:

```python
# ❌ Bad - returns raw data
def get_model(model_id):
    result = db.execute(text('SELECT * FROM models WHERE id = :id'), {'id': model_id})
    return result.fetchone()

# ✅ Good - returns standardized data
def get_model(model_id):
    result = db.execute(text('SELECT * FROM models WHERE id = :id'), {'id': model_id})
    raw_data = result.fetchone()
    return standardize_model_response(raw_data)
```

### 2. Validate at Development Time

Use validation functions during development to catch issues early:

```python
def my_function():
    result = get_model_data(1)
    
    # Validate during development
    if not validate_model_structure(result):
        raise ValueError("Invalid model structure returned")
    
    return result
```

### 3. Use Type Hints

Always use type hints in your function signatures:

```python
def get_model_type(model_id: int) -> Dict[str, Any]:
    """Get model type with consistent structure."""
    # Implementation
```

### 4. Log Validation Results

Use the logging functions to track validation:

```python
from type_utils import validate_and_log_response

def my_function():
    result = get_data()
    validate_and_log_response(result, "model_type")
    return result
```

## Migration Strategy

### For Existing Functions

1. **Identify functions** that return model_type or model data
2. **Add imports** for type utilities
3. **Wrap return values** with standardization functions
4. **Add validation** calls
5. **Test thoroughly** to ensure no breaking changes

### Example Migration

```python
# Before
def get_person_data(person_id):
    result = db.execute(text('SELECT get_model_full(:id)'), {'id': person_id})
    return result.fetchone()[0]

# After
def get_person_data(person_id):
    result = db.execute(text('SELECT get_model_full(:id)'), {'id': person_id})
    raw_data = result.fetchone()[0]
    
    standardized_data = standardize_model_full_data_response(raw_data)
    validate_and_log_response(standardized_data, "model_full_data")
    
    return standardized_data
```

## Testing

### Unit Tests

Create unit tests to verify type consistency:

```python
import unittest
from model_types import validate_model_type_structure

class TestTypeConsistency(unittest.TestCase):
    def test_model_type_structure(self):
        data = {
            "base_model": {"id": 1, "name": "Person", "description": "A person"},
            "traits": [{"id": 1, "name": "Employee", "description": "Works for company"}]
        }
        self.assertTrue(validate_model_type_structure(data))
    
    def test_invalid_model_type_structure(self):
        data = {"invalid": "structure"}
        self.assertFalse(validate_model_type_structure(data))
```

### Integration Tests

Test that your functions return the expected structure:

```python
def test_get_person_details_returns_consistent_structure():
    result = get_person_details(1)
    
    # Check top-level structure
    assert "model" in result
    assert "model_type" in result
    assert "attributes" in result
    assert "relations" in result
    
    # Check model_type structure
    model_type = result["model_type"]
    assert "base_model" in model_type
    assert "traits" in model_type
    
    # Validate the structure
    assert validate_model_full_data_structure(result)
```

## Benefits

1. **Consistency**: All functions return the same structure
2. **Predictability**: Developers know what to expect
3. **Maintainability**: Changes to structure are centralized
4. **Debugging**: Validation helps catch issues early
5. **Documentation**: Types serve as living documentation
6. **IDE Support**: Better autocomplete and error detection

## Conclusion

By following this guide, you can ensure that all database functions return consistent, well-typed data structures. This makes your API more reliable, maintainable, and developer-friendly.

Remember to:
- Always use standardization functions
- Validate your data structures
- Use type hints
- Test your type consistency
- Document your custom types
