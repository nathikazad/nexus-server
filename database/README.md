# GraphQL API with PostGraphile + SQLAlchemy + PostgreSQL

This is a GraphQL-first database API using PostGraphile to automatically generate GraphQL schema from SQLAlchemy models.

## Features

- ✅ **GraphQL API**: Automatic schema generation from database models
- ✅ **PostGraphile**: Zero-config GraphQL server with real-time subscriptions
- ✅ **SQLAlchemy Models**: Type-safe database models with relationships
- ✅ **Alembic Migrations**: Database schema versioning and migrations
- ✅ **GraphiQL Interface**: Interactive GraphQL query interface
- ✅ **Flexible Queries**: Request exactly the data you need

## Project Structure

```
database/
├── config.py               # Database configuration
├── models/                 # SQLAlchemy models
│   ├── __init__.py        # Package initialization
│   └── models.py          # Database model definitions
├── admin_functions/        # Database management scripts
│   ├── init.py            # Database initialization
│   ├── reset_db.py        # Database reset utilities
│   └── load_data.py       # Sample data loading
├── graphql/               # GraphQL API server
│   ├── server.js          # PostGraphile server
│   ├── package.json       # Node.js dependencies
│   ├── gql/               # GraphQL queries
│   │   └── models.gql     # Model queries with fragments
│   └── README.md          # GraphQL setup guide
├── alembic/               # Database migrations
│   ├── env.py             # Alembic environment
│   └── versions/          # Migration files
└── README.md              # This file
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd /Users/nathikazad/Projects/Nexus/server
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
cd /Users/nathikazad/Projects/Nexus/server/database/graphql
npm install
```

### 3. Install PostgreSQL

**On macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 3. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE nexus_db;

# Create user (optional)
CREATE USER nexus_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE nexus_db TO nexus_user;

# Exit
\q
```

### 4. Configure Environment

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your database credentials
nano .env
```

Example `.env` file:
```env
# Local PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nexus_db
DB_USER=postgres
DB_PASSWORD=your_password

# For remote PostgreSQL:
# DB_HOST=your-remote-host.com
# DB_PORT=5432
# DB_NAME=your_database_name
# DB_USER=your_username
# DB_PASSWORD=your_password
```

## Running the Demo

### Option 1: Run the Complete Demo

```bash
cd /Users/nathikazad/Projects/Nexus/server/database
python demo.py
```

This will:
1. Test database connection
2. Run all migrations
3. Add sample data
4. Demonstrate CRUD operations
5. Show migration history

### Option 2: Manual Migration Commands

```bash
cd /Users/nathikazad/Projects/Nexus/server/database

# Run migrations
alembic upgrade head

# Show migration history
alembic history

# Show current revision
alembic current

# Create a new migration (after modifying models)
alembic revision --autogenerate -m "Description of changes"
```

## Migration Files Explained

### 0001_initial_migration.py
Creates the initial `users` table with:
- `id` (Primary Key)
- `name` (String, 100 chars, not null)
- `email` (String, 120 chars, unique, not null)
- `created_at` (DateTime, auto-generated)

### 0002_add_age_column.py
Adds an `age` column to the `users` table:
- `age` (Integer, nullable)

## Database Operations

The demo script shows:

1. **Creating Records**:
```python
user = User(name="Alice", email="alice@example.com", age=28)
db.add(user)
db.commit()
```

2. **Querying Records**:
```python
# Get all users
users = db.query(User).all()

# Filter users
older_users = db.query(User).filter(User.age > 30).all()
```

3. **Updating Records**:
```python
user = db.query(User).filter(User.email == "alice@example.com").first()
user.age = 29
db.commit()
```

## Configuration Options

### Local Development
- Uses `localhost` as default host
- Default port `5432`
- Database name: `nexus_db`
- User: `postgres`

### Remote Database
Update the `.env` file with your remote database credentials:
```env
DB_HOST=your-remote-host.com
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

## Troubleshooting

### Connection Issues
1. Ensure PostgreSQL is running: `brew services list | grep postgresql`
2. Check if database exists: `psql -l | grep nexus_db`
3. Verify credentials in `.env` file

### Migration Issues
1. Check Alembic configuration in `alembic.ini`
2. Ensure database URL is correct in `config.py`
3. Verify migration files are in `alembic/versions/`

### Permission Issues
1. Ensure database user has proper permissions
2. Check PostgreSQL user roles and grants

## Using the GraphQL API

### 5. Start the GraphQL Server

```bash
cd /Users/nathikazad/Projects/Nexus/server/database/graphql
npm start
```

The server will be available at:
- **GraphQL endpoint**: http://localhost:5001/graphql
- **GraphiQL interface**: http://localhost:5001/graphiql

### 6. Query Your Data

Use the GraphiQL interface or make HTTP requests:

```bash
# Get all models with their relationships
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "{ allModels { nodes { id title modelTypeByModelTypeId { name } } } }"}' \
  http://localhost:5001/graphql
```

### 7. Use GraphQL Fragments

Check out `graphql/gql/models.gql` for reusable query fragments:
- `ModelComplete` - All model data
- `ModelBasic` - Basic model info
- `ModelTraits` - Model traits
- `ModelAttributes` - Model attributes
- `ModelOutgoingRelations` - Outgoing relationships
- `ModelIncomingRelations` - Incoming relationships

## Next Steps

This GraphQL-first setup provides:
- ✅ **Automatic API generation** from your database schema
- ✅ **Flexible queries** - request exactly what you need
- ✅ **Real-time subscriptions** for live data updates
- ✅ **Type-safe queries** with automatic validation
- ✅ **Interactive documentation** via GraphiQL
- ✅ **Easy client integration** with any GraphQL client
