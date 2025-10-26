"""
Dice MCP Server

This server implements the Model Context Protocol (MCP) with a simple dice rolling tool
that can roll a dice from 0 to 100. Supports both CORS-HTTP and SSE modes via command line arguments.
"""

import argparse
import logging
import random
import threading
import time
from typing import Dict, Any

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP as FastMCPSSE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_instructions = """
This MCP server provides a simple dice rolling capability.
Use the roll_dice tool to roll a dice and get a random number from 0 to 100.
"""


async def roll_dice() -> Dict[str, Any]:
    """
    Roll a dice and get a random number from 0 to 100.

    Returns:
        Dictionary with 'result' key containing the rolled number and 'range' 
        indicating the possible range (0-100).
    """
    # Generate random number from 0 to 100 (inclusive)
    result = random.randint(0, 100)
    
    logger.info(f"Dice rolled: {result}")
    
    return {
        "result": result,
        "range": "0-100",
        "message": f"You rolled a {result}!"
    }


def create_http_mcp_server():
    """Create and configure the HTTP MCP server with dice rolling tool."""
    # Initialize the FastMCP server for HTTP
    mcp = FastMCP("Dice", stateless_http=True, json_response=True)

    # Register the shared roll_dice function
    mcp.tool()(roll_dice)

    return mcp


def create_sse_mcp_server():
    """Create and configure the SSE MCP server with dice rolling tool."""
    # Initialize the FastMCP server for SSE
    mcp = FastMCPSSE(name="Dice MCP Server", instructions=server_instructions)

    # Register the shared roll_dice function
    mcp.tool()(roll_dice)

    return mcp


def run_cors_http_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the MCP server in CORS-HTTP mode."""
    logger.info("Starting Dice MCP server with CORS support")
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
    logger.info("Starting Dice MCP server in SSE mode")
    logger.info(f"SSE server will be accessible on {host}:{port}")
    logger.info("SSE server will be accessible via SSE transport")
    
    # Create the MCP server
    server = create_sse_mcp_server()
    
    try:
        # Use FastMCP's built-in run method with SSE transport
        server.run(transport="sse", host=host, port=port)
    except KeyboardInterrupt:
        logger.info("SSE server stopped by user")
    except Exception as e:
        logger.error(f"SSE server error: {e}")
        raise


def run_both_servers(cors_host: str = "0.0.0.0", cors_port: int = 8000, 
                    sse_host: str = "0.0.0.0", sse_port: int = 8001):
    """Run both CORS-HTTP and SSE servers simultaneously."""
    logger.info("Starting Dice MCP servers in dual mode")
    logger.info(f"CORS-HTTP server: {cors_host}:{cors_port}")
    logger.info(f"SSE server: {sse_host}:{sse_port}")
    
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
        description="Dice MCP Server - A simple dice rolling MCP server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dice_server.py                    # Run both servers (default)
  python dice_server.py --mode both        # Run both servers explicitly
  python dice_server.py --mode cors-http   # Run only CORS-HTTP server
  python dice_server.py --mode sse         # Run only SSE server
  python dice_server.py --cors-port 8000 --sse-port 8001  # Custom ports for both
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
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
