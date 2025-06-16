"""
QuerySense Phase 2: Complete AI Service with Database Support
GPU-accelerated semantic search with document storage
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from sqlalchemy.orm import Session
import time
import numpy as np
import io
import json
from contextlib import asynccontextmanager

from config_simple import settings
from app.database_simple import get_db, create_tables, Document, QueryHistory, test_connection
from app.embedding_service import EmbeddingService
from app.document_processor import DocumentProcessor
from app.answer_generation_ai import AIAnswerGenerationService

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Global services
embedding_service: Optional[EmbeddingService] = None
document_processor: Optional[DocumentProcessor] = None
answer_service: Optional[AIAnswerGenerationService] = None

# Pydantic models
class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    text: str
    embedding: List[float]
    dimension: int
    model: str

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

class SimilarityResponse(BaseModel):
    text1: str
    text2: str
    similarity: float
    model: str

class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.2

class QueryResponse(BaseModel):
    query: str
    answer: Optional[str]  # Generated answer
    answer_source: Optional[str]  # Source filename for the answer
    results: List[Dict[str, Any]]
    total_results: int
    response_time_ms: int

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    global embedding_service, document_processor, answer_service
    
    logger.info("🚀 Starting QuerySense AI Service Phase 2")
    logger.info(f"🎯 Using device: {settings.device}")
    
    # Test database connection
    if not test_connection():
        logger.error("❌ Database connection failed")
        raise Exception("Database connection failed")
    
    # Create database tables
    create_tables()
    logger.info("📊 Database tables created/verified")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    logger.info("🧠 Embedding service initialized")
      # Initialize document processor
    document_processor = DocumentProcessor()
    logger.info("📄 Document processor initialized")
    
    # Initialize answer generation service
    answer_service = AIAnswerGenerationService(device=settings.device)
    answer_service.initialize()
    logger.info("🤖 Answer generation service initialized")
    
    # Log model information
    model_info = embedding_service.get_model_info()
    logger.info(f"🤖 Model: {model_info['model_name']}")
    logger.info(f"🎮 GPU: {model_info['gpu_name']}")
    logger.info(f"📐 Dimension: {model_info['dimension']}")
    
    yield
    
    logger.info("🛑 Shutting down QuerySense AI Service")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="QuerySense AI Service",
    description="Phase 2: AI-Powered Semantic Search with Local Models",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    model_info = embedding_service.get_model_info() if embedding_service else {}
    return {
        "service": "QuerySense AI Service",
        "version": "2.0.0",
        "status": "running",
        "phase": "2 - AI-Powered Semantic Search",
        "gpu_available": model_info.get("gpu_available", False),
        "gpu_name": model_info.get("gpu_name", "Unknown"),
        "model": model_info.get("model_name", "Unknown")
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    model_info = embedding_service.get_model_info() if embedding_service else {}
    db_status = "connected" if test_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "ai_service": "ready" if embedding_service else "not_ready",
        "database": db_status,
        "model_info": model_info
    }

@app.post("/embed", response_model=EmbedResponse)
async def create_embedding(request: EmbedRequest):
    """Generate embedding for text"""
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Embedding service not available")
    
    try:
        embedding = embedding_service.encode_text(request.text)
        model_info = embedding_service.get_model_info()
        
        return EmbedResponse(
            text=request.text,
            embedding=embedding.tolist(),
            dimension=len(embedding),
            model=model_info["model_name"]
        )
    except Exception as e:
        logger.error(f"❌ Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """Calculate semantic similarity between two texts"""
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Embedding service not available")
    
    try:
        embedding1 = embedding_service.encode_text(request.text1)
        embedding2 = embedding_service.encode_text(request.text2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        model_info = embedding_service.get_model_info()
        
        return SimilarityResponse(
            text1=request.text1,
            text2=request.text2,
            similarity=float(similarity),
            model=model_info["model_name"]
        )
    except Exception as e:
        logger.error(f"❌ Error calculating similarity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating similarity: {str(e)}")

@app.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process documents with AI embeddings"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    if not embedding_service or not document_processor:
        raise HTTPException(status_code=503, detail="AI services not available")
    
    results = []
    
    for file in files:
        try:
            # Read file content
            content = await file.read()
            
            # Process document based on file type
            processed_content = await document_processor.process_file(content, file.filename)
            
            # Generate embedding
            embedding = embedding_service.encode_text(processed_content)
            
            # Save to database
            db_document = Document(
                filename=file.filename,
                content=processed_content,
                file_type=file.content_type or "unknown",
                file_size=len(content),
                embedding=embedding.tolist()  # Convert numpy array to list for JSON storage
            )
            
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            
            results.append(DocumentResponse(
                id=str(db_document.id),
                filename=db_document.filename,
                file_type=db_document.file_type,
                file_size=db_document.file_size,
                upload_timestamp=db_document.upload_timestamp.isoformat()
            ))
            
            logger.info(f"✅ Processed and embedded: {file.filename}")
            
        except Exception as e:
            logger.error(f"❌ Error processing {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
    
    return results

@app.post("/query", response_model=QueryResponse)
async def semantic_search(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Perform semantic search using vector similarity"""
    start_time = time.time()
    
    if not embedding_service:
        raise HTTPException(status_code=503, detail="Embedding service not available")
    
    try:
        # Generate query embedding
        query_embedding = embedding_service.encode_text(request.query)
        
        # Get all documents from database
        documents = db.query(Document).all()
        
        if not documents:
            return QueryResponse(
                query=request.query,
                answer="I couldn't find any documents to answer your question.",
                answer_source=None,
                results=[],
                total_results=0,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Calculate similarities
        similarities = []
        for doc in documents:
            # Convert JSON back to numpy array
            doc_embedding = np.array(doc.embedding)
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            if similarity >= request.similarity_threshold:
                similarities.append({
                    "document": doc,
                    "similarity": float(similarity)
                })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Limit results
        similarities = similarities[:request.max_results]
        
        # Format results
        results = []
        for item in similarities:
            doc = item["document"]
            results.append({
                "id": str(doc.id),
                "filename": doc.filename,
                "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "similarity": item["similarity"],
                "file_type": doc.file_type,
                "upload_timestamp": doc.upload_timestamp.isoformat()
            })        # Generate answer from retrieved documents
        answer_text = None
        answer_source = None
        if answer_service and results:
            answer_result = answer_service.generate_answer(request.query, results)
            if isinstance(answer_result, dict):
                answer_text = answer_result.get("answer")
                answer_source = answer_result.get("source")
            else:
                answer_text = answer_result  # Fallback for string response
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Save query to history
        query_history = QueryHistory(
            query_text=request.query,
            query_embedding=query_embedding.tolist(),
            results_count=len(results),
            response_time_ms=response_time_ms
        )
        db.add(query_history)
        db.commit()
        
        logger.info(f"🔍 Query: '{request.query}' | Results: {len(results)} | Time: {response_time_ms}ms")
        
        return QueryResponse(
            query=request.query,
            answer=answer_text,
            answer_source=answer_source,
            results=results,
            total_results=len(results),
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    return [
        DocumentResponse(
            id=str(doc.id),
            filename=doc.filename,
            file_type=doc.file_type,
            file_size=doc.file_size,
            upload_timestamp=doc.upload_timestamp.isoformat()
        )
        for doc in documents
    ]

@app.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get service statistics"""
    doc_count = db.query(Document).count()
    query_count = db.query(QueryHistory).count()
    
    model_info = embedding_service.get_model_info() if embedding_service else {}
    
    return {
        "documents_stored": doc_count,
        "queries_processed": query_count,
        "model_info": model_info,
        "database_status": "connected" if test_connection() else "disconnected"
    }

@app.get("/documents/{filename}/content")
async def get_document_content(filename: str, db: Session = Depends(get_db)):
    """Get the content of a specific document by filename"""
    document = db.query(Document).filter(Document.filename == filename).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "filename": document.filename,
        "content": document.content,
        "file_type": document.file_type,
        "upload_timestamp": document.upload_timestamp.isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_complete:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
