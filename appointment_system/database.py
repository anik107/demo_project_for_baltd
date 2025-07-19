from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from urllib.parse import quote_plus

# Database connection settings for PostgreSQL
# Get database URL from environment variable or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/appointment_system')

# Handle special characters in password if needed
def get_database_url():
    """Construct database URL with proper encoding"""
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url

    # Fallback to individual environment variables
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('POSTGRES_DB', 'appointment_system')

    # URL encode password to handle special characters
    encoded_password = quote_plus(password)
    return f'postgresql://{user}:{encoded_password}@{host}:{port}/{database}'

SQLALCHEMY_DATABASE_URI = get_database_url()
engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """FastAPI dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()