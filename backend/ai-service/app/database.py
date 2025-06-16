from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
from config import settings

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Vector embedding for semantic search
    embedding = Column(Vector(settings.vector_dimension), nullable=False)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"

class QueryHistory(Base):
    __tablename__ = "query_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(Text, nullable=False)
    query_embedding = Column(Vector(settings.vector_dimension), nullable=False)
    results_count = Column(Integer, nullable=False)
    response_time_ms = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
            return True
    except Exception:
        return False
