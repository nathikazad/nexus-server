# GraphQL API with PostGraphile

This is a GraphQL-first database API using PostGraphile to automatically generate GraphQL schema from SQLAlchemy models.

> **Note**: This is part of the Nexus PKM server. See `../README.md` for the complete system overview.

## Features

- ✅ **GraphQL API**: Automatic schema generation from database models
- ✅ **PostGraphile**: Zero-config GraphQL server with real-time subscriptions
- ✅ **GraphiQL Interface**: Interactive GraphQL query interface
- ✅ **Flexible Queries**: Request exactly the data you need
- ✅ **Real-time subscriptions** for live data updates
- ✅ **Type-safe queries** with automatic validation
- ✅ **Interactive documentation** via GraphiQL
- ✅ **Easy client integration** with any GraphQL client

## Project Structure

```
graphql/
├── server.js              # PostGraphile server
├── package.json           # Node.js dependencies
├── gql/                   # GraphQL queries
│   └── models.gql         # Model queries with fragments
├── env.example            # Environment variables template
└── README.md              # This file
```

## Setup Instructions

### 1. Install Node.js Dependencies

```bash
cd graphql
npm install
```

### 2. Create .env file

```bash
cp env.example .env
# Edit .env with your database settings
```

Example `.env` file:
```env
# GraphQL Server Configuration
NODE_ENV=development
PORT=5001
HOST=0.0.0.0

# Database Configuration (matching your pgdatabase config.py)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexus_db
DB_USER=postgres
DB_PASSWORD=your_password

# Constructed DATABASE_URL for PostGraphile
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/nexus_db
```

### 3. Start the GraphQL Server

```bash
npm start
```

The server will be available at:
- **GraphQL endpoint**: http://localhost:5001/graphql
- **GraphiQL interface**: http://localhost:5001/graphiql

## Usage

### Basic Query Example

```graphql
query {
  allModels {
    nodes {
      id
      title
    }
  }
}
```

### Advanced Query with Relationships

```bash
# Get all models with their relationships
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "{ allModels { nodes { id title modelTypeByModelTypeId { name } } } }"}' \
  http://localhost:5001/graphql
```

### Using GraphQL Fragments

Check out `gql/models.gql` for reusable query fragments:
- `ModelComplete` - All model data
- `ModelBasic` - Basic model info
- `ModelTraits` - Model traits
- `ModelAttributes` - Model attributes
- `ModelOutgoingRelations` - Outgoing relationships
- `ModelIncomingRelations` - Incoming relationships

## Example Queries

### List All Models
```graphql
query GetAllModels {
  allModels {
    nodes {
      id
      title
      body
      createdAt
      updatedAt
    }
  }
}
```

### Get Model with Type Information
```graphql
query GetModelsWithTypes {
  allModels {
    nodes {
      id
      title
      modelTypeByModelTypeId {
        id
        name
        typeKind
        description
      }
    }
  }
}
```

### Get Model by ID
```graphql
query GetModelById($modelId: Int!) {
  modelById(id: $modelId) {
    id
    title
    body
    modelTypeByModelTypeId {
      name
    }
  }
}
```

## Development

### Customizing the Server

Edit `server.js` to:
- Add custom plugins
- Adjust PostGraphile options
- Implement custom middleware

### Available PostGraphile Options

The server is configured with:
- `graphiql: true` - Enable GraphiQL interface
- `enhanceGraphiql: true` - Enhanced GraphiQL features
- `watchPg: true` - Watch for database schema changes
- `subscriptions: true` - Enable real-time subscriptions
- `live: true` - Enable live queries

## Troubleshooting

### Connection Issues
1. Ensure PostgreSQL is running and accessible
2. Check database credentials in `.env` file
3. Verify the database exists and is accessible

### GraphQL Errors
1. Check GraphiQL interface for detailed error messages
2. Verify your query syntax
3. Ensure the requested fields exist in the schema

### Server Issues
1. Check if port 5001 is available
2. Verify Node.js dependencies are installed
3. Check server logs for detailed error messages

## Integration with MCP Server

This GraphQL server is designed to work with the MCP server in the `../mcp/` directory. The MCP server uses the `graphql_client.py` to query this GraphQL API.

### Architecture

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

That's it! PostGraphile automatically generates the entire GraphQL schema from your database tables.