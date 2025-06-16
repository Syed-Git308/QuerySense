"""
Answer Generation Service for QuerySense
Generates direct answers to user questions based on retrieved documents
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class AnswerGenerationService:
    """Service to generate answers from retrieved documents"""
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
    def initialize(self):
        """Initialize the answer generation model"""
        try:
            logger.info("🧠 Initializing answer generation service...")
            
            # Use a lightweight model that works well for Q&A
            model_name = "microsoft/DialoGPT-medium"
            
            # For better question answering, let's use a simpler approach first
            # We'll create a rule-based system that can extract specific information
            logger.info("✅ Answer generation service initialized (rule-based)")
            return True
              except Exception as e:
            logger.error(f"❌ Failed to initialize answer generation: {e}")
            return False
    
    def generate_answer(self, question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a direct answer to the question based on retrieved documents
        Returns both the answer and the source filename
        """
        try:
            if not documents:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question.",
                    "source": None
                }
            
            # Combine all document content
            all_content = "\n\n".join([doc.get("content", "") for doc in documents])
            
            # Use rule-based extraction for common patterns
            answer_result = self._extract_answer_rules(question.lower(), all_content, documents)
            
            if answer_result:
                return answer_result
            
            # Fallback: provide a more focused answer
            most_relevant = documents[0]
            return {
                "answer": f"I found relevant information but couldn't extract a specific answer. The most relevant document discusses {most_relevant.get('filename', 'a document')} with related content.",
                "source": most_relevant.get('filename')
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I encountered an error while generating an answer.",
                "source": None
            }
    
    def _extract_answer_rules(self, question: str, content: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Extract specific answers using rule-based patterns"""
        
        # Find the most relevant document for sourcing
        source_doc = documents[0] if documents else None
        source_filename = source_doc.get('filename') if source_doc else None
        
        # Pattern for employee count questions
        if any(word in question for word in ["employee", "staff", "people", "member", "worker"]):
            if "engineering" in question.lower():
                # Look for engineering employee count
                patterns = [
                    r"engineering.*?employee count.*?(\d+)",
                    r"department:\s*engineering.*?employee count:\s*(\d+)",
                    r"engineering.*?(\d+).*?employee",
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content.lower())
                    if match:
                        count = match.group(1)
                        return {
                            "answer": f"The Engineering department has {count} employees.",
                            "source": source_filename
                        }
            
            # Look for specific department employee counts
            dept_patterns = [
                (r"sales.*?employee count.*?(\d+)", "Sales"),
                (r"marketing.*?employee count.*?(\d+)", "Marketing"),
                (r"hr.*?employee count.*?(\d+)", "HR"),
            ]
            
            for pattern, dept_name in dept_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    count = match.group(1)
                    return {
                        "answer": f"The {dept_name} department has {count} employees.",
                        "source": source_filename
                    }
            
            # General employee count patterns
            employee_patterns = [
                r"employee count:\s*(\d+)",
                r"(\d+)\s*employee",
            ]
            
            for pattern in employee_patterns:
                matches = re.findall(pattern, content.lower())
                if matches:
                    # If multiple matches, try to be more specific
                    if len(matches) == 1:
                        count = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        return {
                            "answer": f"Based on the data, there are {count} employees.",
                            "source": source_filename
                        }
        
        # Pattern for HR/contact questions
        if any(word in question for word in ["hr", "contact", "mail", "email", "orientation"]):
            hr_patterns = [
                r"report to hr at (\d+:\d+\s*[ap]m)",
                r"hr.*?(\d+:\d+\s*[ap]m)",
                r"orientation.*?(\d+:\d+\s*[ap]m)",
            ]
            
            for pattern in hr_patterns:
                match = re.search(pattern, content.lower())
                if match:
                    time = match.group(1)
                    return {
                        "answer": f"Report to HR at {time} for orientation.",
                        "source": source_filename
                    }
        
        # Pattern for budget questions
        if any(word in question for word in ["budget", "cost", "money", "revenue"]):
            if "engineering" in question.lower():
                engineering_budget_patterns = [
                    r"engineering.*?budget.*?(\d+)",
                    r"department:\s*engineering.*?budget.*?(\d+)",
                ]
                
                for pattern in engineering_budget_patterns:
                    match = re.search(pattern, content.lower())
                    if match:
                        amount = match.group(1)
                        return {
                            "answer": f"The Engineering department budget is ${int(amount):,}.",
                            "source": source_filename
                        }
        
        # Pattern for performance/rating questions
        if any(word in question for word in ["performance", "rating", "score"]):
            if "engineering" in question.lower():
                rating_patterns = [
                    r"engineering.*?performance rating:\s*(\w+)",
                    r"department:\s*engineering.*?rating:\s*(\w+)",
                ]
                
                for pattern in rating_patterns:
                    match = re.search(pattern, content.lower())
                    if match:
                        rating = match.group(1).title()
                        return {
                            "answer": f"The Engineering department has a {rating} performance rating.",
                            "source": source_filename
                        }
        
        # Pattern for onboarding/checklist questions
        if any(word in question for word in ["onboard", "checklist", "first day", "orientation", "start"]):
            checklist_patterns = [
                r"first day checklist.*?-\s*(.+?)(?:\n|$)",
                r"## first day.*?\n.*?-\s*(.+?)(?:\n|$)",
            ]
            
            for pattern in checklist_patterns:
                match = re.search(pattern, content.lower(), re.DOTALL)
                if match:
                    item = match.group(1).strip()
                    return {
                        "answer": f"For the first day: {item}",
                        "source": source_filename
                    }
        
        return None
