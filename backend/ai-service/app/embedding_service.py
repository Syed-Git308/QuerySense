import torch
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from config import settings
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """High-performance embedding service using your RTX 4070 Ti"""
    
    def __init__(self):
        self.device = settings.device if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing embedding service on device: {self.device}")
        
        # Load the sentence transformer model
        self.model = SentenceTransformer(settings.embedding_model, device=self.device)
        
        # Optimize for your hardware
        if self.device == "cuda":
            self.model = self.model.half()  # Use FP16 for faster inference on RTX 4070 Ti
            torch.backends.cudnn.benchmark = True
        
        logger.info(f"Loaded embedding model: {settings.embedding_model}")
        logger.info(f"Model dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def encode_text(self, text: str) -> np.ndarray:
        """Encode single text into vector embedding"""
        return self.model.encode([text], convert_to_numpy=True)[0]
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode multiple texts efficiently using batch processing"""
        return self.model.encode(
            texts, 
            batch_size=settings.batch_size,
            convert_to_numpy=True,
            show_progress_bar=False
        )
    
    def compute_similarity(self, query_embedding: np.ndarray, document_embeddings: List[np.ndarray]) -> List[float]:
        """Compute cosine similarity between query and documents"""
        similarities = []
        for doc_embedding in document_embeddings:
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append(float(similarity))
        return similarities
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": settings.embedding_model,
            "device": self.device,
            "dimension": self.model.get_sentence_embedding_dimension(),
            "max_sequence_length": self.model.max_seq_length,
            "cuda_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name() if torch.cuda.is_available() else None
        }
