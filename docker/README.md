# Nexus Docker Setup

This Docker setup provides a complete development and production environment for the Nexus project with PostgreSQL, GraphQL, and MCP servers.

## Features

- **PostgreSQL** with PostGIS, pgvector, trgm, and TimescaleDB extensions
- **GraphQL Server** (Node.js) with PostGraphile
- **MCP Server** (Python) with FastMCP
- **Hot Reload** support for development
- **Multi-platform** support (Mac, Windows, Raspberry Pi)
- **Service Dependencies** with health checks

## Quick Start

### Development (Mac/Windows)

1. **Setup Environment**:
   ```bash
   cd servers
   cp env.dev.example .env.dev
   # Edit .env.dev with your secrets and passwords
   ```

2. **Start Development Environment**:
   ```bash
   cd docker
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file ../.env.dev up --build
   ```

3. **Access Services**:
   - GraphQL: http://localhost:5001
   - GraphiQL: http://localhost:5001/graphiql
   - MCP CORS: http://localhost:8000
   - MCP SSE: http://localhost:8001
   - PostgreSQL: localhost:5433

### Production (Raspberry Pi)

1. **Setup Environment**:
   ```bash
   cd servers
   cp env.prod.example .env.prod
   # Edit .env.prod with your secrets, passwords, and SSD path
   ```

2. **Start Production Environment**:
   ```bash
   cd docker
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ../.env.prod up -d
   ```

## Environment Variables

### Required Variables

- `DB_PASSWORD`: PostgreSQL password
- `GRAPHQL_SECRET`: Secret key for GraphQL server
- `MCP_SECRET`: Secret key for MCP server

### Optional Variables

- `DB_EXTERNAL_PORT`: External PostgreSQL port (default: 5433)
- `GRAPHQL_PORT`: GraphQL server port (default: 5001)
- `MCP_CORS_PORT`: MCP CORS server port (default: 8000)
- `MCP_SSE_PORT`: MCP SSE server port (default: 8001)
- `DATA_PATH`: Data storage path for Raspberry Pi (default: ./data)

## Service Dependencies

1. **PostgreSQL** starts first
2. **GraphQL** waits for PostgreSQL to be healthy
3. **MCP** waits for GraphQL to be healthy

## Hot Reload (Development Only)

- Source code is mounted as volumes
- Changes are reflected immediately without rebuilding
- Node.js and Python servers restart automatically

## Raspberry Pi Optimizations

- Memory limits configured for resource-constrained environments
- Configurable data storage path for SSD mounting
- Production-optimized PostgreSQL settings

## Troubleshooting

### Services won't start
- Check if ports are available
- Verify environment variables are set correctly
- Check Docker logs: `docker-compose logs [service-name]`

### Database connection issues
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Check database credentials in environment file
- Verify network connectivity between services

### Hot reload not working
- Ensure you're using the development compose file
- Check volume mounts in docker-compose.dev.yml
- Verify file permissions

## Commands

```bash
# Start development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml --env-file ../.env.dev up --build

# Start production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml --env-file ../.env.prod up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild specific service
docker-compose build [service-name]

# Access PostgreSQL
docker-compose exec postgres psql -U postgres -d nexus_db
```
