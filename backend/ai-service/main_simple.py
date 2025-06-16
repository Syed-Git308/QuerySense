from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
import time
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

from config_simple import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="QuerySense AI Service",
    description="Phase 2: AI-Powered Semantic Search with Local Models",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
embedding_model: Optional[SentenceTransformer] = None
documents_store = []  # In-memory storage for testing

# Pydantic models for API
class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5
    similarity_threshold: Optional[float] = 0.3

class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    response_time_ms: int

class DocumentUpload(BaseModel):
    content: str
    filename: str

class EmbedRequest(BaseModel):
    text: str

class SimilarityRequest(BaseModel):
    text1: str
    text2: str

class SimilarityResponse(BaseModel):
    text1: str
    text2: str
    similarity: float
    model: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global embedding_model
    
    logger.info("🚀 Starting QuerySense AI Service Phase 2")
    logger.info(f"🎯 Using device: {settings.device}")
    
    # Check GPU availability
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"🎮 GPU detected: {gpu_name}")
    else:
        logger.warning("⚠️ No GPU detected, using CPU")
    
    # Initialize embedding model
    logger.info("🧠 Loading embedding model...")
    embedding_model = SentenceTransformer(settings.embedding_model, device=settings.device)
    logger.info(f"✅ Model loaded: {settings.embedding_model}")
    logger.info(f"📐 Embedding dimension: {embedding_model.get_sentence_embedding_dimension()}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "QuerySense AI Service",
        "version": "2.0.0",
        "status": "running",
        "phase": "2 - AI-Powered Semantic Search",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU",
        "model": settings.embedding_model
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "ai_service": "ready" if embedding_model else "not_ready",
        "gpu": torch.cuda.is_available(),
        "documents_count": len(documents_store),
        "model_info": {
            "name": settings.embedding_model,
            "dimension": embedding_model.get_sentence_embedding_dimension() if embedding_model else None,
            "device": settings.device
        }
    }

@app.post("/add_document")
async def add_document(doc: DocumentUpload):
    """Add a document to the in-memory store"""
    if not embedding_model:
        raise HTTPException(status_code=500, detail="Embedding model not loaded")
    
    try:
        # Generate embedding
        embedding = embedding_model.encode(doc.content)
        
        # Store document
        document = {
            "id": len(documents_store),
            "filename": doc.filename,
            "content": doc.content,
            "embedding": embedding.tolist()
        }
        documents_store.append(document)
        
        logger.info(f"✅ Added document: {doc.filename}")
        return {"message": f"Document '{doc.filename}' added successfully", "id": document["id"]}
        
    except Exception as e:
        logger.error(f"❌ Error adding document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def semantic_search(request: QueryRequest):
    """Perform semantic search using vector similarity"""
    start_time = time.time()
    
    if not embedding_model:
        raise HTTPException(status_code=500, detail="Embedding model not loaded")
    
    try:
        # Generate query embedding
        query_embedding = embedding_model.encode(request.query)
        
        if not documents_store:
            return QueryResponse(
                query=request.query,
                results=[],
                total_results=0,
                response_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Calculate similarities
        similarities = []
        for doc in documents_store:
            doc_embedding = np.array(doc["embedding"])
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
                "id": doc["id"],
                "filename": doc["filename"],
                "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
                "similarity": item["similarity"]
            })
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"🔍 Query: '{request.query}' | Results: {len(results)} | Time: {response_time_ms}ms")
        
        return QueryResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            response_time_ms=response_time_ms
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all documents in memory"""
    return {
        "documents": [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "content_length": len(doc["content"])
            }
            for doc in documents_store
        ],
        "total": len(documents_store)
    }

@app.post("/embed")
async def generate_embedding(request: EmbedRequest):
    """Generate embeddings for text using the AI model"""
    if not embedding_model:
        raise HTTPException(status_code=500, detail="Embedding model not loaded")
    
    try:
        # Generate embedding
        embedding = embedding_model.encode(request.text)
        
        return {
            "text": request.text,
            "embedding": embedding.tolist(),
            "dimension": len(embedding),
            "model": settings.embedding_model
        }
        
    except Exception as e:
        logger.error(f"❌ Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """Calculate semantic similarity between two texts"""
    try:
        # Generate embeddings for both texts
        embedding1 = embedding_model.encode(request.text1)
        embedding2 = embedding_model.encode(request.text2)
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        logger.info(f"🔍 Similarity between '{request.text1}' and '{request.text2}': {similarity:.4f}")
        
        return SimilarityResponse(
            text1=request.text1,
            text2=request.text2,
            similarity=float(similarity),
            model=settings.embedding_model
        )
        
    except Exception as e:
        logger.error(f"❌ Error calculating similarity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating similarity: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
