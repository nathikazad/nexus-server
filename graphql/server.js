const express = require('express');
const { postgraphile } = require('postgraphile');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Enable CORS
app.use(cors());

// Simple database URL construction
const dbUrl = process.env.DATABASE_URL || 
  `postgresql://${process.env.DB_USER || 'postgres'}:${process.env.DB_PASSWORD || 'password'}@${process.env.DB_HOST || 'localhost'}:${process.env.DB_PORT || '5432'}/${process.env.DB_NAME || 'nexus_db'}`;

// PostGraphile middleware - the magic happens here!
app.use(postgraphile(dbUrl, 'public', {
  graphiql: true,
  enhanceGraphiql: true,
}));

const PORT = process.env.PORT || 5001;

app.listen(PORT, () => {
  console.log(`🚀 GraphQL server running on http://localhost:${PORT}`);
  console.log(`📊 GraphiQL interface: http://localhost:${PORT}/graphiql`);
});
