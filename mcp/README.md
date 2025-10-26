# MCP Server - HTTP API Usage

This directory contains the MCP (Model Context Protocol) server implementation with GraphQL integration.

> **Note**: This is part of the Nexus PKM server. See `../README.md` for the complete system overview.

## Files

- `pkm_server_new.py` - Main MCP server with PKM database functions
- `dice_server.py` - Dice rolling MCP server
- `graphql_client.py` - GraphQL client for database operations
- `handlers/` - Modular handlers for different function categories
  - `people_handler.py` - People-related database operations

## Prerequisites

1. **Install Python Dependencies**:
   ```bash
   cd mcp
   pip install -r requirements.txt
   ```

2. **GraphQL Server** must be running:
   ```bash
   cd ../graphql
   npm start
   ```
   Server runs on: http://localhost:5001

3. **MCP Server** must be running:
   ```bash
   cd mcp
   python pkm_server_new.py
   ```
   Server runs on: http://localhost:8000

## HTTP API Usage with curl

### Basic Request Format

All MCP function calls use JSON-RPC 2.0 format:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "FUNCTION_NAME",
      "arguments": {}
    },
    "id": 1
  }' \
  http://localhost:8000/mcp
```

### Available Functions

#### 1. List People
Get all people in the knowledge base:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "list_people",
      "arguments": {}
    },
    "id": 1
  }' \
  http://localhost:8000/mcp
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{"type": "text", "text": "..."}],
    "structuredContent": {
      "result": {
        "people": [
          {
            "id": 1,
            "name": "Alice Johnson",
            "description": "Software engineer with 5 years experience"
          }
        ],
        "count": 1,
        "message": "Found 1 people in your knowledge base"
      }
    },
    "isError": false
  }
}
```

#### 2. Add People
Add new people to the knowledge base:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add_people",
      "arguments": {
        "people": [
          {
            "name": "John Doe",
            "description": "Software developer"
          }
        ]
      }
    },
    "id": 2
  }' \
  http://localhost:8000/mcp
```

#### 3. Get Person Details
Get comprehensive details for a specific person:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_person_details",
      "arguments": {
        "person_id": 1
      }
    },
    "id": 3
  }' \
  http://localhost:8000/mcp
```

### Error Handling

If a function call fails, you'll receive an error response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32600,
    "message": "Not Acceptable: Client must accept both application/json and text/event-stream"
  }
}
```

### Common Issues

1. **"Not Acceptable" Error**: Make sure to include both headers:
   - `Content-Type: application/json`
   - `Accept: application/json, text/event-stream`

2. **Connection Refused**: Ensure both servers are running:
   - GraphQL server on port 5001
   - MCP server on port 8000

3. **Function Not Found**: Check that the function name is correct and the server is running the latest version.

### Testing the Setup

1. **Test GraphQL Server**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"query": "{ allModels { nodes { id title } } }"}' \
     http://localhost:5001/graphql
   ```

2. **Test MCP Server**:
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_people", "arguments": {}}, "id": 1}' \
     http://localhost:8000/mcp
   ```

## Development

### Adding New Functions

1. Create a new handler in `handlers/` directory
2. Import and register the function in `pkm_server_new.py`
3. Update this README with the new function's usage

### GraphQL Integration

The server uses GraphQL queries defined in `../graphql/gql/models.gql`. The `graphql_client.py` automatically:
- Extracts queries and fragments from the .gql file
- Combines them into complete GraphQL requests
- Handles the HTTP communication with the GraphQL server

## Architecture

```
┌─────────────────┐    HTTP/JSON-RPC    ┌─────────────────┐
│   Client        │ ──────────────────► │   MCP Server    │
│   (curl, etc.)  │                     │   (port 8000)   │
└─────────────────┘                     └─────────────────┘
                                                 │
                                                 │ GraphQL
                                                 ▼
                                        ┌─────────────────┐
                                        │ GraphQL Server  │
                                        │ (port 5001)     │
                                        └─────────────────┘
                                                 │
                                                 │ SQL
                                                 ▼
                                        ┌─────────────────┐
                                        │ PostgreSQL DB   │
                                        └─────────────────┘
```
