import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://querysense:querysense123@localhost:5432/querysense_ai"
      # AI Models - Upgraded for RTX 4070 Ti (12GB VRAM)
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"  # Much better embeddings
    device: str = "cuda"  # Your RTX 4070 Ti
    batch_size: int = 16  # Optimized for larger models
    max_sequence_length: int = 512
    
    # AI Answer Generation - Production Grade Models
    openai_api_key: str = ""
    use_local_ai: bool = True
    qa_model: str = "microsoft/deberta-v3-large-squad2"  # State-of-the-art Q&A
    text_gen_model: str = "microsoft/DialoGPT-medium"  # Better text generation
    
    # Alternative high-performance models for your RTX 4070 Ti
    # Uncomment these for even better performance:
    # qa_model: str = "deepset/deberta-v3-large-squad2"  # Best accuracy
    # text_gen_model: str = "microsoft/DialoGPT-large"  # Best generation
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:3001"]
      # Vector Search - Optimized for accuracy
    vector_dimension: int = 768  # mpnet-base-v2 uses 768 dimensions
    similarity_threshold: float = 0.2  # Lower threshold for better recall
    max_results: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
