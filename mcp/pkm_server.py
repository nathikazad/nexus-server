"""
PKM (Personal Knowledge Management) MCP Server

This server provides access to the PKM database for LLM agents using GraphQL.
"""

import argparse
import logging
import sys
import os
from typing import Dict, Any
import time  # ✅ added

import uvicorn
from starlette.middleware.cors import CORSMiddleware
from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP as FastMCPSSE

# Add handlers to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handlers.people_handler import list_people, add_people, get_person_details

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_instructions = """
This MCP server provides access to your Personal Knowledge Management (PKM) database via GraphQL.
Use the available tools to:
- list_people: Get all people in your knowledge base
- add_people: Add new people to your knowledge base
- get_person_details: Get comprehensive details for a specific person by ID
"""


def create_http_mcp_server():
    """Create and configure the HTTP MCP server with PKM tools."""
    mcp = FastMCP("PKM Server", stateless_http=True, json_response=True)
    
    # Register the PKM functions
    mcp.tool()(list_people)
    mcp.tool()(add_people)
    mcp.tool()(get_person_details)
    
    return mcp


def create_sse_mcp_server():
    """Create and configure the SSE MCP server with PKM tools."""
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
    
    mcp = create_http_mcp_server()
    starlette_app = mcp.streamable_http_app()
    
    # Add CORS middleware
    starlette_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Suppress verbose MCP logging
    logging.getLogger("mcp.server.streamable_http").setLevel(logging.CRITICAL + 1)
    
    uvicorn.run(starlette_app, host=host, port=port)


def run_sse_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the MCP server in SSE mode."""
    logger.info("Starting PKM MCP server in SSE mode")
    logger.info(f"SSE server will be accessible on {host}:{port}")
    
    server = create_sse_mcp_server()
    
    try:
        server.run(transport="sse", host=host, port=port)
    except KeyboardInterrupt:
        logger.info("SSE server stopped by user")
    except Exception as e:
        logger.error(f"SSE server error: {e}")
        raise


def main():
    """Main function to start the MCP server."""
    parser = argparse.ArgumentParser(
        description="PKM MCP Server - GraphQL-based Personal Knowledge Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pkm_server.py                    # Run both servers (default)
  python pkm_server.py --mode cors-http   # Run only CORS-HTTP server
  python pkm_server.py --mode sse         # Run only SSE server
  python pkm_server.py --reload           # Watch for file changes and auto-restart
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["both", "cors-http", "sse"],
        default="both",
        help="Server mode (default: both)"
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

    # ✅ NEW: reload argument
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload when Python files change (dev only)"
    )
    
    args = parser.parse_args()

    # ✅ NEW: setup file watcher if reload is enabled
    if args.reload:
        try:
            from watchdog.observers import Observer
            from watchdog.events import PatternMatchingEventHandler
        except ImportError:
            logger.error("❌ 'watchdog' not installed. Run `pip install watchdog`.")
            sys.exit(1)

        class ReloadHandler(PatternMatchingEventHandler):
            def __init__(self):
                super().__init__(patterns=["*.py"], ignore_directories=True)
            def on_modified(self, event):
                logger.info(f"🔁 Change detected in {event.src_path}. Restarting server...")
                os.execv(sys.executable, [sys.executable] + sys.argv)

        observer = Observer()
        handler = ReloadHandler()
        observer.schedule(handler, ".", recursive=True)
        observer.start()
        logger.info("👀 Watching for Python file changes (reload mode enabled)...")
    
    try:
        if args.mode == "both":
            import threading
            
            cors_thread = threading.Thread(
                target=run_cors_http_server, 
                args=(args.host, args.cors_port),
                daemon=True
            )
            
            sse_thread = threading.Thread(
                target=run_sse_server, 
                args=(args.host, args.sse_port),
                daemon=True
            )
            
            cors_thread.start()
            time.sleep(1)
            sse_thread.start()
            
            logger.info("Both servers started successfully!")
            logger.info("Press Ctrl+C to stop both servers")
            
            cors_thread.join()
            sse_thread.join()
            
        elif args.mode == "sse":
            run_sse_server(host=args.host, port=args.sse_port)
        else:  # cors-http mode
            run_cors_http_server(host=args.host, port=args.cors_port)
            
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        if args.reload:
            observer.stop()
            observer.join()


if __name__ == "__main__":
    main()
