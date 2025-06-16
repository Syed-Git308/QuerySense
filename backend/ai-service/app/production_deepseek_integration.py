"""
Production DeepSeek Integration for QuerySense
Drop-in replacement for your current answer generator
"""
import logging
from typing import List, Dict, Any
from .enhanced_deepseek_generator import EnhancedDeepSeekGenerator
from .deepseek_models_comparison import get_recommendation

logger = logging.getLogger(__name__)

class ProductionDeepSeekAnswerGenerator:
    """Production-ready DeepSeek integration for QuerySense"""
    
    def __init__(self, model_preference: str = None):
        """
        Initialize with automatic model selection
        
        Args:
            model_preference: Specific model to use, or None for auto-selection
        """
        self.generator = None
        self.model_preference = model_preference
        self.is_initialized = False
        
        logger.info("🌊 Production DeepSeek Answer Generator initialized")
    
    def initialize(self):
        """Initialize the DeepSeek model with error handling"""
        try:
            # Auto-select best model if none specified
            if self.model_preference:
                self.generator = EnhancedDeepSeekGenerator(
                    preferred_model=self.model_preference
                )
            else:
                # Auto-select based on maximum accuracy
                self.generator = EnhancedDeepSeekGenerator(
                    use_case="maximum_accuracy"
                )
            
            self.generator.initialize()
            self.is_initialized = True
            
            model_info = self.generator.get_model_info()
            logger.info(f"✅ DeepSeek ready: {model_info['model_name']}")
            logger.info(f"🎯 Expected accuracy: {model_info.get('accuracy', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize DeepSeek: {e}")
            logger.info("🔄 Falling back to rule-based answers")
            self.is_initialized = False
    
    def generate_answer(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate answer using DeepSeek or fallback to rule-based
        
        Compatible with existing QuerySense answer generator interface
        """
        if not self.is_initialized or not self.generator:
            logger.warning("DeepSeek not available, using fallback")
            return self._rule_based_fallback(query, documents)
        
        try:
            # Use DeepSeek for generation
            response = self.generator.generate_answer(query, documents)
            
            # Add QuerySense-specific metadata
            response.update({
                "generator_type": "DeepSeek",
                "model_family": "DeepSeek",
                "enhanced": True
            })
            
            logger.info(f"✅ DeepSeek answer generated (confidence: {response.get('confidence', 0):.1%})")
            return response
            
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            return self._rule_based_fallback(query, documents)
    
    def _rule_based_fallback(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback to rule-based answers when DeepSeek fails"""
        
        if not documents:
            return {
                "answer": "No documents available to answer your question.",
                "confidence": 0.0,
                "source": None,
                "generator_type": "Fallback",
                "model_family": "Rule-based"
            }
        
        query_lower = query.lower()
        document = documents[0]
        content = document.get('content', '').lower()
        filename = document.get('filename', 'Unknown')
        
        # Enhanced rule-based patterns
        import re
        
        # Vacation days
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
                        "source": filename,
                        "generator_type": "Rule-based",
                        "model_family": "Pattern matching"
                    }
        
        # Department employee counts
        elif 'employee' in query_lower and ('most' in query_lower or 'biggest' in query_lower):
            content_raw = document.get('content', '')
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
                    "source": filename,
                    "generator_type": "Rule-based",
                    "model_family": "CSV parsing"
                }
        
        # Specific department counts
        elif 'how many' in query_lower and 'department' in query_lower:
            # Extract department name from query
            dept_match = re.search(r'\\b([A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*)\\s+department', query, re.IGNORECASE)
            if dept_match:
                target_dept = dept_match.group(1).strip()
                
                content_raw = document.get('content', '')
                lines = content_raw.split('\\n')
                
                for line in lines[1:]:  # Skip header
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 2 and target_dept.lower() in parts[0].lower():
                        try:
                            emp_count = int(parts[1])
                            return {
                                "answer": f"The {parts[0]} department has {emp_count} employees.",
                                "confidence": 0.9,
                                "source": filename,
                                "generator_type": "Rule-based",
                                "model_family": "CSV parsing"
                            }
                        except:
                            continue
        
        # Generic content search
        else:
            # Simple keyword matching
            keywords = [word for word in query_lower.split() if len(word) > 3]
            relevant_sentences = []
            
            sentences = content.split('.')
            for sentence in sentences:
                if any(keyword in sentence.lower() for keyword in keywords):
                    relevant_sentences.append(sentence.strip())
            
            if relevant_sentences:
                answer = '. '.join(relevant_sentences[:2])
                return {
                    "answer": answer + '.',
                    "confidence": 0.6,
                    "source": filename,
                    "generator_type": "Rule-based",
                    "model_family": "Keyword matching"
                }
        
        return {
            "answer": "I found relevant information but couldn't extract a specific answer. Please try rephrasing your question.",
            "confidence": 0.3,
            "source": filename,
            "generator_type": "Rule-based",
            "model_family": "Fallback"
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model information"""
        if self.is_initialized and self.generator:
            return self.generator.get_model_info()
        else:
            return {
                "model_name": "Rule-based fallback",
                "model_family": "Traditional",
                "status": "fallback_active",
                "accuracy": "60-80%",
                "vram_usage_gb": 0
            }
    
    def switch_model(self, new_model: str):
        """Switch to a different DeepSeek model"""
        if self.is_initialized and self.generator:
            try:
                self.generator.switch_model(new_model)
                logger.info(f"✅ Switched to {new_model}")
            except Exception as e:
                logger.error(f"❌ Failed to switch model: {e}")
        else:
            logger.warning("Cannot switch model - DeepSeek not initialized")


# Factory function for easy integration
def create_deepseek_generator(model_preference: str = None) -> ProductionDeepSeekAnswerGenerator:
    """
    Factory function to create a production DeepSeek generator
    
    Usage:
        # Auto-select best model
        generator = create_deepseek_generator()
        
        # Use specific model
        generator = create_deepseek_generator("deepseek-ai/deepseek-llm-7b-chat")
    """
    return ProductionDeepSeekAnswerGenerator(model_preference)


# Integration example for main.py
"""
To integrate into your main.py, replace your current answer generator with:

from app.production_deepseek_integration import create_deepseek_generator

# Initialize DeepSeek generator
answer_generator = create_deepseek_generator()
answer_generator.initialize()

# Use in your endpoint
@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query = data.get('query')
    
    # Your existing document search
    documents = db.search_documents(query, limit=3)
    
    # Generate answer with DeepSeek
    response = answer_generator.generate_answer(query, documents)
    
    return jsonify(response)
"""
