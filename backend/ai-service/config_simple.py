import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # AI Models
    embedding_model: str = "all-MiniLM-L6-v2"
    device: str = "cuda"  # Your RTX 4070 Ti
    batch_size: int = 32
    max_sequence_length: int = 512
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
      # Vector Search
    vector_dimension: int = 384
    similarity_threshold: float = 0.2
    max_results: int = 10
    
    # Logging
    log_level: str = "INFO"
      # Database (disabled for now)
    use_database: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Allow extra fields from .env

settings = Settings()
