# QuerySense Phase 2: AI Service Setup

## Prerequisites
- Python 3.9+ 
- PostgreSQL 15+
- CUDA 11.8+ (for RTX 4070 Ti)

## Quick Setup

### 1. Python Environment
```bash
# Create virtual environment
cd backend/ai-service
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. PostgreSQL Setup
```sql
-- Connect to PostgreSQL and run:
CREATE DATABASE querysense_ai;
CREATE USER querysense WITH PASSWORD 'querysense123';
GRANT ALL PRIVILEGES ON DATABASE querysense_ai TO querysense;

-- Enable pgvector extension
\c querysense_ai
CREATE EXTENSION vector;
```

### 3. Start AI Service
```bash
python main.py
```

## API Endpoints

### Health Check
- GET `/health` - Service status and model info

### Document Upload
- POST `/upload` - Upload documents with AI embedding
- Returns: Document metadata with embeddings stored

### Semantic Search  
- POST `/query` - AI-powered semantic search
- Body: `{"query": "your question", "max_results": 5}`
- Returns: Ranked results with similarity scores

### Document Management
- GET `/documents` - List all documents

## Features

### ⚡ Performance Optimizations
- **GPU Acceleration**: Uses your RTX 4070 Ti for embedding generation
- **FP16 Inference**: Faster processing with half-precision
- **Batch Processing**: Efficient multi-document processing
- **Vector Database**: PostgreSQL + pgvector for fast similarity search

### 🧠 AI Capabilities
- **Semantic Search**: Understands meaning, not just keywords
- **Context Awareness**: Finds relevant content even without exact matches
- **Multi-format Support**: txt, csv, docx, xlsx, json, md
- **Similarity Scoring**: Ranked results with confidence scores

### 📊 Model Information
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Size**: ~90MB (fast download)
- **Performance**: ~1000 texts/sec on RTX 4070 Ti
- **Quality**: Excellent for semantic search tasks

## Example Usage

### Upload Document
```bash
curl -X POST "http://localhost:8001/upload" \
     -F "files=@document.pdf"
```

### Semantic Query
```bash
curl -X POST "http://localhost:8001/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "employee headcount by department"}'
```

This will find relevant content even if the document uses different terms like "staff count" or "workforce distribution"!
