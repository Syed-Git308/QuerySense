"""
Enhanced DeepSeek Answer Generator - Multi-Model Support for RTX 4070 Ti
Supports DeepSeek R1, LLM, and Coder series with automatic model selection
"""
import os
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    BitsAndBytesConfig, pipeline
)
import logging
import re
from .deepseek_models_comparison import DEEPSEEK_MODELS_RTX_4070TI, get_recommendation, OPTIMAL_SETTINGS

logger = logging.getLogger(__name__)

class EnhancedDeepSeekGenerator:
    """Enhanced DeepSeek with multi-model support and smart model selection"""
    
    def __init__(self, preferred_model: str = None, use_case: str = "maximum_accuracy"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_case = use_case
        
        # Auto-select best model if none specified
        if preferred_model:
            self.model_name = preferred_model
        else:
            recommendation = get_recommendation(use_case)
            self.model_name = recommendation["primary"]
            logger.info(f"🎯 Auto-selected {self.model_name} for {use_case}")
        
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.model_info = DEEPSEEK_MODELS_RTX_4070TI.get(self.model_name, {})
        
        logger.info(f"🌊 Initializing {self.model_name} on {self.device}")
        
    def initialize(self):
        """Initialize DeepSeek model with RTX 4070 Ti optimization"""
        try:
            logger.info(f"🔥 Loading {self.model_name}...")
            logger.info(f"📊 Expected VRAM: {self.model_info.get('vram_required', 'Unknown')}")
            logger.info(f"🎯 Accuracy: {self.model_info.get('accuracy', 'Unknown')}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                use_fast=True
            )
            
            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Configure quantization for larger models
            model_config = self._get_model_config()
              # Load model with optimized settings
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_config
            )
            
            # Create optimized pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device_map="auto",
                return_full_text=False
            )
            
            logger.info("✅ DeepSeek loaded successfully!")
            if torch.cuda.is_available():
                vram_used = torch.cuda.memory_allocated(0) / 1024**3
                logger.info(f"💾 VRAM Usage: {vram_used:.1f}GB")
                
                # Warn if close to limit
                if vram_used > 10:
                    logger.warning(f"⚠️ High VRAM usage ({vram_used:.1f}GB). Consider using 4-bit quantization.")
            
        except Exception as e:
            logger.error(f"❌ Failed to load {self.model_name}: {e}")
            logger.info("🔄 Attempting fallback to smaller model...")
            self._try_fallback_model()
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Get optimized model configuration based on model size and VRAM"""
        config = {
            "torch_dtype": torch.float16,
            "device_map": "auto",
            "trust_remote_code": True,
            "low_cpu_mem_usage": True
        }
        
        # Check if we need quantization
        vram_required = self.model_info.get('vram_required', '8GB')
        vram_gb = float(re.search(r'(\d+)', vram_required).group(1))
        
        if vram_gb > 8 or "V3" in self.model_name:
            logger.info("🔧 Applying 4-bit quantization for large model")
            config["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        
        return config
    
    def _try_fallback_model(self):
        """Try to load a smaller model if the primary fails"""
        fallback_models = [
            "deepseek-ai/deepseek-llm-7b-chat",
            "deepseek-ai/deepseek-coder-6.7b-instruct"
        ]
        
        for fallback in fallback_models:
            if fallback != self.model_name:
                logger.info(f"🔄 Trying fallback: {fallback}")
                self.model_name = fallback
                self.model_info = DEEPSEEK_MODELS_RTX_4070TI.get(fallback, {})
                try:
                    self.initialize()
                    return
                except:
                    continue
        
        raise RuntimeError("Failed to load any DeepSeek model")
    
    def generate_answer(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate precise answers using DeepSeek's reasoning capabilities"""
        
        if not documents:
            return {
                "answer": "No documents available to answer your question. Please upload relevant documents first.",
                "confidence": 0.0,
                "source": None,
                "model_used": self.model_name
            }
        
        # Prepare optimized context
        context = self._prepare_context(documents, query)
        
        # Create model-specific prompt
        prompt = self._create_optimized_prompt(query, context)
        
        try:            # Generate with DeepSeek
            response = self.pipeline(
                prompt,
                max_new_tokens=self._get_optimal_tokens(query),
                temperature=0.1 if "data" in query.lower() else 0.2,
                do_sample=True,
                top_p=0.85,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract clean answer
            answer = self._extract_clean_answer(response[0]['generated_text'])
            confidence = self._calculate_confidence(answer, query, documents)
            
            return {
                "answer": answer,
                "confidence": confidence,
                "source": documents[0].get('filename', 'Unknown'),
                "model_used": self.model_name,
                "model_accuracy": self.model_info.get('accuracy', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"DeepSeek generation error: {e}")
            return self._fallback_answer(query, documents)
    
    def _prepare_context(self, documents: List[Dict[str, Any]], query: str) -> str:
        """Prepare context optimized for the specific DeepSeek model"""
        contexts = []
        
        # Use more documents for R1 models (better reasoning)
        max_docs = 3 if "R1" in self.model_name else 2
        
        for i, doc in enumerate(documents[:max_docs]):
            content = doc.get('content', '')
            filename = doc.get('filename', f'Doc{i+1}')
            
            # Clean and structure the content
            cleaned_content = self._clean_content(content, query)
            contexts.append(f"[Source: {filename}]\\n{cleaned_content}")
        
        return "\\n\\n".join(contexts)
    
    def _clean_content(self, content: str, query: str) -> str:
        """Clean content with query-aware optimization"""
        # Remove excessive whitespace
        content = re.sub(r'\\s+', ' ', content)
        
        # Query-specific length optimization
        if "coder" in self.model_name.lower() and any(word in query.lower() for word in ["csv", "data", "number", "count"]):
            # Keep more data for CSV analysis
            max_length = 1500
        elif "R1" in self.model_name:
            # R1 models can handle longer context
            max_length = 2000
        else:
            max_length = 1000
        
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content.strip()
    
    def _create_optimized_prompt(self, query: str, context: str) -> str:
        """Create model-specific optimized prompt"""
        
        # Different prompt styles for different models
        if "R1" in self.model_name:
            return self._create_r1_prompt(query, context)
        elif "coder" in self.model_name.lower():
            return self._create_coder_prompt(query, context)
        else:
            return self._create_chat_prompt(query, context)
    
    def _create_r1_prompt(self, query: str, context: str) -> str:
        """R1-specific prompt for advanced reasoning"""
        return f"""<|im_start|>system
You are an expert business analyst with access to company documents. Analyze the provided information carefully and give precise, well-reasoned answers.
<|im_end|>

<|im_start|>user
Documents:
{context}

Question: {query}

Please analyze the documents and provide a clear, accurate answer. If the question involves data analysis, show your reasoning step by step.
<|im_end|>

<|im_start|>assistant"""
    
    def _create_coder_prompt(self, query: str, context: str) -> str:
        """Coder-specific prompt for data analysis"""
        return f"""# Business Data Analysis Task

## Available Data:
{context}

## Query: {query}

## Analysis:
Based on the provided data, I need to:"""
    
    def _create_chat_prompt(self, query: str, context: str) -> str:
        """General chat prompt for standard Q&A"""
        return f"""You are a helpful AI assistant that provides accurate answers based on business documents.

Documents:
{context}

Question: {query}

Please provide a clear, specific answer based on the information in the documents.

Answer:"""
    
    def _get_optimal_tokens(self, query: str) -> int:
        """Get optimal token count based on query type"""
        if any(word in query.lower() for word in ["list", "all", "every", "breakdown"]):
            return 256  # Longer answers for comprehensive questions
        elif any(word in query.lower() for word in ["how many", "what is", "when"]):
            return 128  # Shorter for factual questions
        else:
            return 192  # Medium for general questions
    
    def _extract_clean_answer(self, generated_text: str) -> str:
        """Extract and clean the answer from DeepSeek output"""
        
        answer = generated_text.strip()
        
        # Model-specific cleaning
        if "R1" in self.model_name:
            # R1 models may have structured output
            if "Analysis:" in answer:
                answer = answer.split("Analysis:")[-1].strip()
        
        # Remove common prefixes
        prefixes_to_remove = [
            "Answer:", "Response:", "Based on the documents:", "According to the information:",
            "The answer is:", "Assistant:", "AI:", "Analysis:", "Based on the provided data,"
        ]
        
        for prefix in prefixes_to_remove:
            if answer.startswith(prefix):
                answer = answer[len(prefix):].strip()
        
        # Clean up and format
        answer = re.sub(r'\\n+', ' ', answer)  # Replace newlines with spaces
        answer = re.sub(r'\\s+', ' ', answer)  # Normalize whitespace
        
        # Take first complete sentence for factual questions
        sentences = answer.split('.')
        if len(sentences) > 1 and len(sentences[0]) > 20:
            answer = sentences[0] + '.'
        
        # Ensure proper ending
        if answer and not answer.endswith(('.', '!', '?')):
            answer += '.'
        
        return answer if answer else "I need more specific information to provide an accurate answer."
    
    def _calculate_confidence(self, answer: str, query: str, documents: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on answer quality and model capabilities"""
        base_confidence = float(self.model_info.get('accuracy', '90%').rstrip('%')) / 100
        
        # Adjust based on answer quality
        if len(answer) < 10:
            return base_confidence * 0.5
        elif "I need more" in answer or "cannot find" in answer.lower():
            return base_confidence * 0.3
        elif any(word in answer.lower() for word in ["specifically", "exactly", "according to"]):
            return min(0.98, base_confidence * 1.05)
        else:
            return base_confidence
    
    def _fallback_answer(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced fallback with model info"""
        # Use the existing fallback logic but add model info
        query_lower = query.lower()
        content = documents[0].get('content', '').lower()
        
        # Enhanced pattern matching
        if 'vacation' in query_lower and ('day' in query_lower or 'time' in query_lower):
            patterns = [
                r'(\\d+)\\s*days?.*(?:per|each).*year',
                r'(\\d+)\\s*vacation\\s*days?',
                r'annual.*leave.*?(\\d+)\\s*days?'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    return {
                        "answer": f"Employees receive {match.group(1)} vacation days per year according to the policy.",
                        "confidence": 0.85,
                        "source": documents[0].get('filename'),
                        "model_used": f"{self.model_name} (fallback)"
                    }
        
        elif 'employee' in query_lower and ('most' in query_lower or 'biggest' in query_lower or 'largest' in query_lower):
            # Enhanced CSV parsing
            content_raw = documents[0].get('content', '')
            lines = content_raw.split('\\n')
            
            departments = {}
            for line in lines[1:]:  # Skip header
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    try:
                        dept = parts[0]
                        emp_count = int(parts[1])
                        departments[dept] = emp_count
                    except:
                        continue
            
            if departments:
                max_dept = max(departments.items(), key=lambda x: x[1])
                return {
                    "answer": f"The {max_dept[0]} department has the most employees with {max_dept[1]} people.",
                    "confidence": 0.9,
                    "source": documents[0].get('filename'),
                    "model_used": f"{self.model_name} (fallback)"
                }
        
        return {
            "answer": "I found relevant information but couldn't extract a specific answer. Please try rephrasing your question.",
            "confidence": 0.3,
            "source": documents[0].get('filename') if documents else None,
            "model_used": f"{self.model_name} (fallback)"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive DeepSeek model information"""
        info = {
            "model_name": self.model_name,
            "model_family": "DeepSeek",
            "use_case": self.use_case,
            "status": "loaded" if self.model else "not_loaded",
            **self.model_info
        }
        
        if torch.cuda.is_available() and self.model:
            info["vram_usage_gb"] = torch.cuda.memory_allocated(0) / 1024**3
        
        return info
    
    def switch_model(self, new_model: str):
        """Switch to a different DeepSeek model"""
        logger.info(f"🔄 Switching from {self.model_name} to {new_model}")
        
        # Clean up current model
        if self.model:
            del self.model
            del self.tokenizer
            del self.pipeline
            torch.cuda.empty_cache()
        
        # Load new model
        self.model_name = new_model
        self.model_info = DEEPSEEK_MODELS_RTX_4070TI.get(new_model, {})
        self.initialize()
