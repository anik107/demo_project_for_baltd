from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# Database connection settings for PostgreSQL
# e.g.: postgresql://username:password@localhost:5432/dbname
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/appointment_system'
engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()