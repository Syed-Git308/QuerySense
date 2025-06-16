"""
Database module for QuerySense AI Service - PostgreSQL without pgvector
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config_simple import settings
import json
from datetime import datetime

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://querysense:querysense123@localhost:5432/querysense_ai"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    embedding = Column(JSON, nullable=False)  # Store as JSON array
    upload_timestamp = Column(DateTime, server_default=func.now())

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(JSON, nullable=False)  # Store as JSON array
    results_count = Column(Integer)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime, server_default=func.now())

# Database functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).scalar()
        db.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
