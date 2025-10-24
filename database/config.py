import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Database configuration with support for local and remote PostgreSQL"""
    
    def __init__(self):
        # Default to local PostgreSQL
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'nexus_db')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'password')
        
    @property
    def database_url(self):
        """Generate database URL for SQLAlchemy"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def alembic_database_url(self):
        """Generate database URL for Alembic (without echo)"""
        return self.database_url

# Create global config instance
db_config = DatabaseConfig()
