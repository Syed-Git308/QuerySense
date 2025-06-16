-- QuerySense Phase 2: Database Setup
-- Run this script in PostgreSQL to set up the AI service database

-- Create database and user
CREATE DATABASE querysense_ai;
CREATE USER querysense WITH PASSWORD 'querysense123';
GRANT ALL PRIVILEGES ON DATABASE querysense_ai TO querysense;

-- Connect to the new database
\c querysense_ai

-- Enable the pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant permissions
GRANT ALL ON SCHEMA public TO querysense;

-- Verify setup
SELECT version();
SELECT * FROM pg_extension WHERE extname = 'vector';
