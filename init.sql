-- Database initialization script for appointment system
-- This script will be executed when the PostgreSQL container starts for the first time

-- Create the database if it doesn't exist (this is usually handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS appointment_system;

-- Connect to the appointment_system database
\c appointment_system;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE appointment_system TO postgres;

-- You can add any initial data or additional setup here
-- For example, creating initial admin user, seeding data, etc.

-- Print completion message
\echo 'Database initialization completed successfully!'
