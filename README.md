# Nexus Server

This is the server component of the Nexus Personal Knowledge Management (PKM) system. It provides a GraphQL API and MCP (Model Context Protocol) server for accessing and managing your knowledge base.

## Architecture

```
┌─────────────────┐    HTTP/JSON-RPC    ┌─────────────────┐
│   Client        │ ──────────────────► │   MCP Server    │
│   (Mobile App,  │                     │   (port 8000)   │
│   Web App, etc.)│                     └─────────────────┘
└─────────────────┘                              │
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

## Components

### 🗄️ **pgdatabase/** - PostgreSQL Database
- **SQLAlchemy Models**: Type-safe database models with relationships
- **Alembic Migrations**: Database schema versioning and migrations
- **Database Management**: Admin functions for initialization and data loading
- **PostgreSQL Integration**: Full PostgreSQL database support

### 🌐 **graphql/** - GraphQL API Server
- **PostGraphile**: Zero-config GraphQL server with real-time subscriptions
- **Automatic Schema Generation**: GraphQL schema generated from database models
- **GraphiQL Interface**: Interactive GraphQL query interface
- **Flexible Queries**: Request exactly the data you need

### 🔌 **mcp/** - MCP Server
- **FastMCP**: High-performance MCP server implementation
- **GraphQL Integration**: Uses GraphQL client to query the database
- **Modular Handlers**: Separate handlers for different function categories
- **HTTP API**: RESTful API for external clients

## Quick Start

### 1. Database Setup
```bash
cd pgdatabase
pip install -r requirements.txt
# Follow pgdatabase/README.md for database setup
```

### 2. GraphQL Server
```bash
cd graphql
npm install
npm start
# Server runs on http://localhost:5001
```

### 3. MCP Server
```bash
cd mcp
pip install -r requirements.txt
python pkm_server_new.py
# Server runs on http://localhost:8000
```

## API Endpoints

### GraphQL API (Port 5001)
- **GraphQL Endpoint**: http://localhost:5001/graphql
- **GraphiQL Interface**: http://localhost:5001/graphiql

### MCP API (Port 8000)
- **MCP Endpoint**: http://localhost:8000/mcp
- **Available Functions**: `list_people`, `add_people`, `get_person_details`

## Example Usage

### GraphQL Query
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "{ allModels { nodes { id title } } }"}' \
  http://localhost:5001/graphql
```

### MCP Function Call
```bash
curl -X POST -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "list_people", "arguments": {}}, "id": 1}' \
  http://localhost:8000/mcp
```

## Development

### Adding New Functions
1. Create a new handler in `mcp/handlers/`
2. Register the function in `mcp/pkm_server_new.py`
3. Update `mcp/README.md` with usage examples

### Database Changes
1. Modify models in `pgdatabase/models/`
2. Create migration: `cd pgdatabase && alembic revision --autogenerate -m "Description"`
3. Apply migration: `alembic upgrade head`

### GraphQL Schema Changes
- PostGraphile automatically updates the GraphQL schema when database changes
- Update queries in `graphql/gql/models.gql` as needed

## Documentation

- **Database**: See `pgdatabase/README.md` for PostgreSQL setup and management
- **GraphQL**: See `graphql/README.md` for GraphQL API usage and examples
- **MCP**: See `mcp/README.md` for MCP server functions and HTTP API usage

## Requirements

- **Python 3.8+**
- **Node.js 16+**
- **PostgreSQL 12+**

## License

This project is part of the Nexus PKM system.
