"""
Quick performance boost for QuerySense - Immediate improvements
This script will reset your database and upload test documents with better models
"""
import os
import sys
import logging
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, Document, SessionLocal
from app.embedding_service import EmbeddingService
from app.document_processor import DocumentProcessor
from config import settings
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reset_and_improve_system():
    """Reset the system with better configuration"""
    
    logger.info("🔄 Resetting QuerySense for better performance...")
    
    # Step 1: Drop and recreate tables with correct dimensions
    logger.info("📊 Resetting database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Step 2: Initialize services
    logger.info("🧠 Initializing embedding service...")
    embedding_service = EmbeddingService()
    document_processor = DocumentProcessor()
    
    # Step 3: Upload test documents
    test_files = [
        "../../test-vacation-policy.txt",
        "../../test-onboarding-guide.txt", 
        "../../test-company-data.csv"
    ]
    
    db = SessionLocal()
    
    for file_path in test_files:
        if os.path.exists(file_path):
            logger.info(f"📄 Processing {file_path}...")
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process content
            processed_content = await document_processor.process_file(
                content.encode('utf-8'), 
                os.path.basename(file_path)
            )
            
            # Generate embedding
            embedding = embedding_service.encode_text(processed_content)
            
            # Save to database
            doc = Document(
                filename=os.path.basename(file_path),
                content=processed_content,
                file_type="text/plain" if file_path.endswith('.txt') else "text/csv",
                file_size=len(content),
                embedding=embedding.tolist()
            )
            
            db.add(doc)
            logger.info(f"✅ Added {os.path.basename(file_path)} with {len(embedding)} dimensions")
    
    db.commit()
    db.close()
    
    logger.info("🎉 System reset complete! Your QuerySense should now perform much better.")
    logger.info("📋 Test with these questions:")
    logger.info("   - How many vacation days do new employees get?")
    logger.info("   - What time should I report on my first day?")
    logger.info("   - Which department has the highest budget?")

if __name__ == "__main__":
    asyncio.run(reset_and_improve_system())
