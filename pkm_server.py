"""
PKM (Personal Knowledge Management) MCP Server

This server provides access to the PKM database for LLM agents.
It exposes functions to list and add people to the knowledge base.

The server uses the graph document schema with:
- ModelType: "Person" for people
- Model: Individual person records with title (name) and body (description)
- Attributes: Additional metadata as needed
"""

import argparse
import logging
import sys
import os
from typing import Dict, Any, List, Optional

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP as FastMCPSSE

# Add database directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

from models import SessionLocal, Model, ModelType, engine
from config import db_config
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_instructions = """
This MCP server provides access to your Personal Knowledge Management (PKM) database.
Use the available tools to:
- list_people: Get all people in your knowledge base with their names and descriptions
- add_people: Add new people to your knowledge base with name and description
- get_person_details: Get comprehensive details for a specific person by ID, including traits, attributes, and relationships
"""


async def list_people() -> Dict[str, Any]:
    """
    List all people in the PKM database.
    
    Returns:
        Dictionary with 'people' key containing a list of people, each with 'name' and 'description'.
        Returns empty list if no people found or if database is not initialized.
    """
    try:
        # Test database connection first
        with engine.connect() as conn:
            pass  # Connection test
        
        db = SessionLocal()
        try:
            # Find the Person model type
            person_type = db.query(ModelType).filter(
                ModelType.name == "Person",
                ModelType.type_kind == "base"
            ).first()
            
            if not person_type:
                logger.warning("Person model type not found. Database may not be initialized.")
                return {
                    "people": [],
                    "message": "No Person model type found. Please run database initialization first.",
                    "count": 0
                }
            
            # Get all people (models of type Person)
            people_models = db.query(Model).filter(
                Model.model_type_id == person_type.id
            ).all()
            
            people_list = []
            for person in people_models:
                people_list.append({
                    "id": person.id,
                    "name": person.title,
                    "description": person.body or "No description available"
                })
            
            logger.info(f"Retrieved {len(people_list)} people from database")
            
            return {
                "people": people_list,
                "count": len(people_list),
                "message": f"Found {len(people_list)} people in your knowledge base"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error listing people: {e}")
        return {
            "people": [],
            "error": str(e),
            "message": "Failed to retrieve people from database. Please check database connection.",
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
        # Test database connection first
        with engine.connect() as conn:
            pass  # Connection test
        
        db = SessionLocal()
        try:
            # Find or create the Person model type
            person_type = db.query(ModelType).filter(
                ModelType.name == "Person",
                ModelType.type_kind == "base"
            ).first()
            
            if not person_type:
                # Create Person model type if it doesn't exist
                person_type = ModelType(
                    name="Person",
                    type_kind="base",
                    description="A human person in the knowledge base"
                )
                db.add(person_type)
                db.commit()
                db.refresh(person_type)
                logger.info("Created Person model type")
            
            # Check if person with this name already exists
            existing_person = db.query(Model).filter(
                Model.model_type_id == person_type.id,
                Model.title == name.strip()
            ).first()
            
            if existing_person:
                return {
                    "success": False,
                    "error": "Person already exists",
                    "message": f"A person named '{name}' already exists in your knowledge base",
                    "existing_person": {
                        "name": existing_person.title,
                        "description": existing_person.body or "No description"
                    }
                }
            
            # Create new person
            new_person = Model(
                model_type_id=person_type.id,
                title=name.strip(),
                body=description.strip() if description else None
            )
            
            db.add(new_person)
            db.commit()
            db.refresh(new_person)
            
            logger.info(f"Added new person: {name}")
            
            return {
                "success": True,
                "person": {
                    "id": str(new_person.id),
                    "name": new_person.title,
                    "description": new_person.body or "No description"
                },
                "message": f"Successfully added '{name}' to your knowledge base"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error adding person: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to add person to database. Please check database connection."
        }


async def get_person_details(person_id: int) -> Dict[str, Any]:
    """
    Get comprehensive details for a specific person by their ID.
    
    This function uses the PostgreSQL get_model_full function to retrieve:
    - Basic model information (name, description, etc.)
    - Model type information
    - All traits assigned to the person
    - All attributes and their values
    - All relationships (both incoming and outgoing) with related models
    
    Args:
        person_id: The ID of the person/model to retrieve details for
    
    Returns:
        Dictionary with comprehensive person details including model data, traits, 
        attributes, and relationships. Returns error information if person not found.
    """
    try:
        # Test database connection first
        with engine.connect() as conn:
            pass  # Connection test
        
        db = SessionLocal()
        try:
            # First verify the model exists
            model = db.query(Model).filter(Model.id == person_id).first()
            
            if not model:
                return {
                    "success": False,
                    "error": "Person not found",
                    "message": f"No person found with ID {person_id}",
                    "person_id": person_id
                }
            
            # Use the PostgreSQL function to get comprehensive data
            result = db.execute(text('SELECT get_model_full(:person_id)'), {'person_id': person_id})
            full_data = result.fetchone()[0]
            
            if not full_data:
                return {
                    "success": False,
                    "error": "Failed to retrieve person data",
                    "message": f"Could not retrieve data for person ID {person_id}",
                    "person_id": person_id
                }
            
            logger.info(f"Retrieved comprehensive data for person {person_id}")
            
            return {
                "success": True,
                "person_id": person_id,
                "data": full_data,
                "message": f"Successfully retrieved comprehensive details for person {person_id}"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting person details for ID {person_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to retrieve person details for ID {person_id}. Please check database connection.",
            "person_id": person_id
        }


def create_http_mcp_server():
    """Create and configure the HTTP MCP server with PKM tools."""
    # Initialize the FastMCP server for HTTP
    mcp = FastMCP("PKM Server", stateless_http=True, json_response=True)

    # Register the PKM functions
    mcp.tool()(list_people)
    mcp.tool()(add_people)
    mcp.tool()(get_person_details)

    return mcp


def create_sse_mcp_server():
    """Create and configure the SSE MCP server with PKM tools."""
    # Initialize the FastMCP server for SSE
    mcp = FastMCPSSE(name="PKM MCP Server", instructions=server_instructions)

    # Register the PKM functions
    mcp.tool()(list_people)
    mcp.tool()(add_people)
    mcp.tool()(get_person_details)

    return mcp


def run_cors_http_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the MCP server in CORS-HTTP mode."""
    logger.info("Starting PKM MCP server with CORS support")
    logger.info(f"CORS-HTTP server will be accessible on {host}:{port}")
    
    # Create the MCP server
    mcp = create_http_mcp_server()
    
    # Get the Starlette app for streamable HTTP
    starlette_app = mcp.streamable_http_app()
    
    # Add CORS middleware
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development; restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Suppress verbose MCP logging
    logging.getLogger("mcp.server.streamable_http").setLevel(logging.CRITICAL + 1)
    
    # Run the server
    uvicorn.run(starlette_app, host=host, port=port)


def run_sse_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the MCP server in SSE mode."""
    logger.info("Starting PKM MCP server in SSE mode")
    logger.info(f"SSE server will be accessible on {host}:{port}")
    logger.info("SSE server will be accessible via SSE transport")
    
    # Create the MCP server
    server = create_sse_mcp_server()
    
    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host=host, port=port)
    except KeyboardInterrupt:
        logger.info("SSE server stopped by person")
    except Exception as e:
        logger.error(f"SSE server error: {e}")
        raise


def run_both_servers(cors_host: str = "0.0.0.0", cors_port: int = 8000, 
                    sse_host: str = "0.0.0.0", sse_port: int = 8001):
    """Run both CORS-HTTP and SSE servers simultaneously."""
    logger.info("Starting PKM MCP servers in dual mode")
    logger.info(f"CORS-HTTP server: {cors_host}:{cors_port}")
    logger.info(f"SSE server: {sse_host}:{sse_port}")
    
    import threading
    import time
    
    # Create threads for both servers
    cors_thread = threading.Thread(
        target=run_cors_http_server, 
        args=(cors_host, cors_port),
        daemon=True
    )
    
    sse_thread = threading.Thread(
        target=run_sse_server, 
        args=(sse_host, sse_port),
        daemon=True
    )
    
    try:
        # Start both servers
        cors_thread.start()
        time.sleep(1)  # Small delay to ensure CORS server starts first
        sse_thread.start()
        
        logger.info("Both servers started successfully!")
        logger.info("Press Ctrl+C to stop both servers")
        
        # Wait for both threads to complete
        cors_thread.join()
        sse_thread.join()
        
    except KeyboardInterrupt:
        logger.info("Stopping both servers...")
    except Exception as e:
        logger.error(f"Error running servers: {e}")
        raise


def main():
    """Main function to start the MCP server with command line arguments."""
    parser = argparse.ArgumentParser(
        description="PKM MCP Server - Access to Personal Knowledge Management database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pkm_server.py                    # Run both servers (default)
  python pkm_server.py --mode both        # Run both servers explicitly
  python pkm_server.py --mode cors-http   # Run only CORS-HTTP server
  python pkm_server.py --mode sse         # Run only SSE server
  python pkm_server.py --cors-port 8002 --sse-port 8003  # Custom ports for both

Available Tools:
  - list_people: Get all people in your knowledge base
  - add_people: Add new people with name and description
  - get_person_details: Get comprehensive details for a specific person by ID
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["both", "cors-http", "sse"],
        default="both",
        help="Server mode: 'both' for both servers, 'cors-http' for CORS-HTTP only, or 'sse' for SSE only (default: both)"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind the servers to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--cors-port",
        type=int,
        default=8000,
        help="Port for CORS-HTTP server (default: 8000)"
    )
    
    parser.add_argument(
        "--sse-port",
        type=int,
        default=8001,
        help="Port for SSE server (default: 8001)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "both":
            run_both_servers(
                cors_host=args.host, 
                cors_port=args.cors_port,
                sse_host=args.host, 
                sse_port=args.sse_port
            )
        elif args.mode == "sse":
            run_sse_server(host=args.host, port=args.sse_port)
        else:  # cors-http mode
            run_cors_http_server(host=args.host, port=args.cors_port)
    except KeyboardInterrupt:
        logger.info("Server stopped by person")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
