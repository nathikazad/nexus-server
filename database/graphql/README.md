# Simple PostGraphile Server

The simplest possible PostGraphile setup to list models from your PKM database.

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Create .env file:**
```bash
cp env.example .env
# Edit .env with your database settings
```

3. **Start the server:**
```bash
npm start
```

## Usage

- **GraphQL endpoint:** http://localhost:5001/graphql
- **GraphiQL interface:** http://localhost:5001/graphiql

## Query to list models:

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

That's it! PostGraphile automatically generates the entire GraphQL schema from your database tables.