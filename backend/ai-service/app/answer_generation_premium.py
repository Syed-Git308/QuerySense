"""
Premium AI-Powered Answer Generation Service for QuerySense
Designed to outperform paid LLM APIs with RTX 4070 Ti optimization
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import re
import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForQuestionAnswering,
    AutoModelForCausalLM, pipeline, 
    T5Tokenizer, T5ForConditionalGeneration
)
import numpy as np
from sentence_transformers import SentenceTransformer
import gc

logger = logging.getLogger(__name__)

class PremiumAnswerGenerationService:
    """Premium AI service optimized for RTX 4070 Ti to achieve better-than-paid-LLM performance"""
    
    def __init__(self, device: str = "cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.qa_model = None
        self.qa_tokenizer = None
        self.reasoning_model = None
        self.reasoning_tokenizer = None
        self.summarizer = None
        
        # Model configurations optimized for RTX 4070 Ti (12GB VRAM)
        self.qa_model_name = "microsoft/deberta-v3-large-squad2"  # State-of-the-art Q&A
        self.reasoning_model_name = "google/flan-t5-large"  # Excellent reasoning
        
        logger.info(f"🎮 Initializing Premium AI service on {self.device}")
        
    def initialize(self):
        """Initialize premium AI models with memory optimization"""
        try:
            logger.info("🧠 Loading premium AI models for RTX 4070 Ti...")
            
            # Load Q&A model with optimization
            logger.info(f"📚 Loading Q&A model: {self.qa_model_name}")
            self.qa_tokenizer = AutoTokenizer.from_pretrained(self.qa_model_name)
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained(
                self.qa_model_name,
                torch_dtype=torch.float16,  # Use half precision for memory efficiency
                device_map="auto"
            )
            
            # Load reasoning model (T5-based for better text generation)
            logger.info(f"🧮 Loading reasoning model: {self.reasoning_model_name}")
            self.reasoning_tokenizer = T5Tokenizer.from_pretrained(self.reasoning_model_name)
            self.reasoning_model = T5ForConditionalGeneration.from_pretrained(
                self.reasoning_model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Create summarization pipeline
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16
            )
            
            logger.info("✅ Premium AI models loaded successfully")
            logger.info(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3}GB available")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize premium AI models: {e}")
            raise
    
    def generate_answer(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate premium quality answers using advanced AI models"""
        try:
            if not documents:
                return {
                    "answer": "I don't have any relevant documents to answer your question. Please upload some documents first.",
                    "confidence": 0.0,
                    "source": None,
                    "reasoning": "No documents available"
                }
            
            # Step 1: Extract and rank relevant contexts
            contexts = self._extract_relevant_contexts(query, documents)
            if not contexts:
                return {
                    "answer": "I couldn't find relevant information in the available documents.",
                    "confidence": 0.1,
                    "source": None,
                    "reasoning": "No relevant contexts found"
                }
            
            # Step 2: Generate answer using Q&A model
            qa_result = self._answer_with_qa_model(query, contexts)
            
            # Step 3: Enhance answer with reasoning model
            enhanced_answer = self._enhance_with_reasoning(query, qa_result, contexts)
            
            # Step 4: Validate and improve answer quality
            final_answer = self._validate_and_improve_answer(enhanced_answer, contexts)
            
            return final_answer
            
        except Exception as e:
            logger.error(f"❌ Error generating answer: {e}")
            return {
                "answer": "I encountered an error while processing your question. Please try rephrasing it.",
                "confidence": 0.0,
                "source": None,
                "reasoning": f"Error: {str(e)}"
            }
    
    def _extract_relevant_contexts(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and rank the most relevant contexts from documents"""
        contexts = []
        
        for doc in documents:
            content = doc.get('content', '')
            filename = doc.get('filename', 'unknown')
            similarity = doc.get('similarity', 0.0)
            
            # Split content into meaningful chunks
            chunks = self._split_into_semantic_chunks(content)
            
            for chunk in chunks:
                if len(chunk.strip()) > 50:  # Only meaningful chunks
                    contexts.append({
                        'text': chunk,
                        'filename': filename,
                        'similarity': similarity,
                        'relevance_score': self._calculate_relevance(query, chunk)
                    })
        
        # Sort by combined similarity and relevance
        contexts.sort(key=lambda x: (x['similarity'] + x['relevance_score']) / 2, reverse=True)
        
        # Return top 3 most relevant contexts
        return contexts[:3]
    
    def _split_into_semantic_chunks(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        
        for para in paragraphs:
            para = para.strip()
            if len(para) > 100:
                # Split long paragraphs by sentences
                sentences = re.split(r'[.!?]+', para)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if len(current_chunk + sentence) < 400:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(para)
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 30]
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """Calculate semantic relevance between query and text"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        # Simple but effective relevance scoring
        common_words = query_words.intersection(text_words)
        if not query_words:
            return 0.0
        
        return len(common_words) / len(query_words)
    
    def _answer_with_qa_model(self, query: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using the Q&A model"""
        best_answer = None
        best_score = 0.0
        best_source = None
        
        for context in contexts:
            try:
                # Prepare input for Q&A model
                inputs = self.qa_tokenizer(
                    query,
                    context['text'],
                    return_tensors="pt",
                    max_length=512,
                    truncation=True,
                    padding=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.qa_model(**inputs)
                    start_scores = outputs.start_logits
                    end_scores = outputs.end_logits
                    
                    # Get the most likely answer
                    start_idx = torch.argmax(start_scores)
                    end_idx = torch.argmax(end_scores) + 1
                    
                    # Calculate confidence score
                    confidence = float(torch.max(start_scores).item() + torch.max(end_scores).item())
                    
                    if confidence > best_score and end_idx > start_idx:
                        # Extract answer text
                        answer_tokens = inputs['input_ids'][0][start_idx:end_idx]
                        answer = self.qa_tokenizer.decode(answer_tokens, skip_special_tokens=True)
                        
                        if len(answer.strip()) > 3:  # Valid answer
                            best_answer = answer.strip()
                            best_score = confidence
                            best_source = context['filename']
                
            except Exception as e:
                logger.warning(f"Error processing context: {e}")
                continue
        
        return {
            "answer": best_answer,
            "confidence": best_score,
            "source": best_source
        }
    
    def _enhance_with_reasoning(self, query: str, qa_result: Dict[str, Any], contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance the answer using reasoning model for better quality"""
        if not qa_result["answer"]:
            return qa_result
        
        try:
            # Create a prompt for the reasoning model
            context_text = " ".join([ctx['text'][:200] for ctx in contexts[:2]])
            
            prompt = f"""
            Question: {query}
            Context: {context_text}
            Initial Answer: {qa_result['answer']}
            
            Please provide a clear, complete, and accurate answer based on the context:
            """
            
            # Generate enhanced answer
            inputs = self.reasoning_tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.reasoning_model.generate(
                    **inputs,
                    max_new_tokens=150,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1
                )
            
            enhanced_answer = self.reasoning_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the actual answer (remove the prompt)
            if "answer:" in enhanced_answer.lower():
                enhanced_answer = enhanced_answer.split("answer:")[-1].strip()
            
            # Use enhanced answer if it's better
            if len(enhanced_answer) > len(qa_result["answer"]) and len(enhanced_answer) < 500:
                qa_result["answer"] = enhanced_answer
                qa_result["confidence"] = min(qa_result["confidence"] * 1.2, 1.0)
            
        except Exception as e:
            logger.warning(f"Error enhancing answer: {e}")
        
        return qa_result
    
    def _validate_and_improve_answer(self, answer_result: Dict[str, Any], contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Final validation and improvement of the answer"""
        answer = answer_result.get("answer", "")
        
        if not answer or len(answer.strip()) < 5:
            return {
                "answer": "I found relevant information but couldn't generate a specific answer. Please try rephrasing your question.",
                "confidence": 0.1,
                "source": contexts[0]['filename'] if contexts else None,
                "reasoning": "Answer too short or empty"
            }
        
        # Clean up the answer
        answer = self._clean_answer(answer)
        
        # Add confidence adjustment based on answer quality
        confidence = self._assess_answer_quality(answer, contexts)
        
        return {
            "answer": answer,
            "confidence": confidence,
            "source": answer_result.get("source"),
            "reasoning": "Generated using premium AI models"
        }
    
    def _clean_answer(self, answer: str) -> str:
        """Clean and format the answer"""
        # Remove common artifacts
        answer = re.sub(r'^(answer:|Answer:)\s*', '', answer, flags=re.IGNORECASE)
        answer = re.sub(r'\s+', ' ', answer)  # Normalize whitespace
        answer = answer.strip()
        
        # Ensure proper sentence structure
        if answer and not answer.endswith(('.', '!', '?')):
            answer += '.'
        
        return answer
    
    def _assess_answer_quality(self, answer: str, contexts: List[Dict[str, Any]]) -> float:
        """Assess the quality of the generated answer"""
        base_confidence = 0.8
        
        # Length check
        if len(answer) < 10:
            base_confidence *= 0.5
        elif len(answer) > 200:
            base_confidence *= 0.9
        
        # Content quality check
        if any(phrase in answer.lower() for phrase in ['i found', 'need more context', 'please try']):
            base_confidence *= 0.3
        
        # Relevance check with contexts
        answer_words = set(answer.lower().split())
        context_words = set()
        for ctx in contexts:
            context_words.update(ctx['text'].lower().split())
        
        if answer_words.intersection(context_words):
            base_confidence *= 1.1
        
        return min(base_confidence, 1.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "qa_model": self.qa_model_name,
            "reasoning_model": self.reasoning_model_name,
            "device": self.device,
            "gpu_memory_gb": torch.cuda.get_device_properties(0).total_memory // 1024**3 if torch.cuda.is_available() else 0,
            "models_loaded": self.qa_model is not None and self.reasoning_model is not None
        }
