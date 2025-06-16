"""
AI-Powered Answer Generation Service for QuerySense
Uses advanced language models to generate human-like, accurate answers
from any document format and structure
"""
import logging
from typing import List, Dict, Any, Optional
import re
import json
import os
from datetime import datetime
import requests
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
import torch

logger = logging.getLogger(__name__)

class AIAnswerGenerationService:
    """Advanced AI service to generate human-like answers from any document type"""
    
    def __init__(self, device: str = "cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.qa_pipeline = None
        self.text_generator = None
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.use_local_model = not self.openai_api_key
        
    def initialize(self):
        """Initialize AI models for answer generation"""
        try:
            logger.info("🧠 Initializing AI answer generation service...")
            
            if self.use_local_model:
                logger.info("🤖 Loading local AI models...")
                
                # Load question-answering model
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model="distilbert-base-cased-distilled-squad",
                    device=0 if self.device == "cuda" else -1
                )
                
                # Load text generation model for more complex reasoning
                self.text_generator = pipeline(
                    "text-generation",
                    model="microsoft/DialoGPT-medium",
                    device=0 if self.device == "cuda" else -1
                )
                
                logger.info("✅ Local AI models loaded successfully")
            else:
                logger.info("🌐 Using OpenAI API for answer generation")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI models: {e}")
            return False
    
    def generate_answer(self, question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate intelligent, context-aware answers using AI
        """
        try:
            if not documents:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question. Please try uploading relevant company documents or rephrasing your question.",
                    "source": None
                }
            
            logger.info(f"🔍 AI analyzing question: '{question}'")
            logger.info(f"📄 Processing {len(documents)} documents")
            
            # Prepare context from all documents
            context = self._prepare_context(documents)
            
            # Generate answer using AI
            if self.openai_api_key and not self.use_local_model:
                answer_result = self._generate_openai_answer(question, context, documents)
            else:
                answer_result = self._generate_local_answer(question, context, documents)
            
            if answer_result:
                logger.info(f"✅ AI generated answer: {answer_result['answer'][:100]}...")
                return answer_result
            
            # Fallback response
            return {
                "answer": "I found relevant information but need more context to provide a specific answer. Could you please rephrase your question or provide more details?",
                "source": documents[0].get('filename') if documents else None
            }
            
        except Exception as e:
            logger.error(f"Error in AI answer generation: {e}")
            return {
                "answer": "I encountered an error while analyzing your question. Please try again or contact support.",
                "source": None
            }
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare comprehensive context from all documents"""
        context_parts = []
        
        for doc in documents:
            filename = doc.get('filename', 'Unknown Document')
            content = doc.get('content', '')
            
            # Add document header
            context_parts.append(f"\n--- {filename} ---")
            
            # Process different document types intelligently
            if filename.endswith('.csv'):
                processed_content = self._process_csv_content(content)
            elif 'onboarding' in filename.lower() or 'guide' in filename.lower():
                processed_content = self._process_guide_content(content)
            elif 'policy' in filename.lower() or 'vacation' in filename.lower():
                processed_content = self._process_policy_content(content)
            else:
                processed_content = content
            
            context_parts.append(processed_content)
        
        return "\n".join(context_parts)
    
    def _process_csv_content(self, content: str) -> str:
        """Process CSV content to make it more readable for AI"""
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return content
        
        # Parse as structured data
        header = lines[0].split(',')
        rows = [line.split(',') for line in lines[1:]]
        
        # Create human-readable format
        formatted_lines = [f"Data contains {len(rows)} records with fields: {', '.join(header)}"]
        
        for i, row in enumerate(rows):
            if len(row) == len(header):
                record_info = []
                for j, value in enumerate(row):
                    if j < len(header):
                        record_info.append(f"{header[j]}: {value.strip()}")
                formatted_lines.append(f"Record {i+1}: {', '.join(record_info)}")
        
        return '\n'.join(formatted_lines)
    
    def _process_guide_content(self, content: str) -> str:
        """Process guide/onboarding content with clear structure"""
        # Add clear markers for important information
        processed = content
        processed = re.sub(r'(\d+[\.\)])(.+)', r'Step \1\2', processed)
        processed = re.sub(r'(checklist|todo|action items?)', r'📋 \1', processed, flags=re.IGNORECASE)
        processed = re.sub(r'(meet with|contact|speak to)', r'👥 \1', processed, flags=re.IGNORECASE)
        processed = re.sub(r'(bring|required|need)', r'📝 \1', processed, flags=re.IGNORECASE)
        return processed
    
    def _process_policy_content(self, content: str) -> str:
        """Process policy content with emphasis on key rules"""
        processed = content
        processed = re.sub(r'(\d+\s*days?)', r'⏰ \1', processed, flags=re.IGNORECASE)
        processed = re.sub(r'(must|required|mandatory)', r'⚠️ \1', processed, flags=re.IGNORECASE)
        processed = re.sub(r'(allowed|permitted|can)', r'✅ \1', processed, flags=re.IGNORECASE)
        return processed
    
    def _generate_openai_answer(self, question: str, context: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate answer using OpenAI API"""
        try:
            import openai
            
            prompt = f"""You are a helpful AI assistant for a company's internal knowledge system. Answer the user's question based on the provided company documents. Be accurate, concise, and helpful.

Company Documents:
{context}

User Question: {question}

Instructions:
- Provide a direct, accurate answer based on the documents
- If you need to analyze data, be specific with numbers and departments
- If information is missing, clearly state what additional info is needed
- Always cite which document your answer came from
- Be conversational and human-like in your response

Answer:"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for company internal knowledge."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Determine best source document
            source = self._determine_source_document(question, documents)
            
            return {
                "answer": answer,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def _generate_local_answer(self, question: str, context: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Generate answer using local AI models"""
        try:
            # Use question-answering pipeline for direct answers
            if len(context) > 4000:  # Truncate if too long
                context = context[:4000] + "..."
            
            result = self.qa_pipeline(question=question, context=context)
            
            if result['score'] > 0.1:  # Confidence threshold
                answer = result['answer']
                
                # Enhance answer with contextual information
                enhanced_answer = self._enhance_answer(question, answer, documents)
                
                source = self._determine_source_document(question, documents)
                
                return {
                    "answer": enhanced_answer,
                    "source": source
                }
            
            # Fallback to pattern-based answering for structured data
            return self._pattern_based_answer(question, documents)
            
        except Exception as e:
            logger.error(f"Local AI model error: {e}")
            return self._pattern_based_answer(question, documents)
    
    def _enhance_answer(self, question: str, base_answer: str, documents: List[Dict[str, Any]]) -> str:
        """Enhance the base answer with additional context and analysis"""
        
        # For data questions, try to add more analytical context
        if any(word in question.lower() for word in ['most', 'least', 'total', 'count', 'budget']):
            csv_docs = [doc for doc in documents if doc.get('filename', '').endswith('.csv')]
            if csv_docs:
                analysis = self._analyze_csv_data(question, csv_docs[0])
                if analysis:
                    return f"{base_answer}. {analysis}"
        
        # For policy questions, add practical guidance
        if any(word in question.lower() for word in ['vacation', 'time off', 'policy']):
            return f"{base_answer} Please check with HR if you need clarification on the specific procedures."
        
        # For onboarding questions, add helpful reminders
        if any(word in question.lower() for word in ['first day', 'onboarding', 'new employee']):
            return f"{base_answer} Don't forget to bring required documents and arrive a few minutes early."
        
        return base_answer
    
    def _analyze_csv_data(self, question: str, csv_doc: Dict[str, Any]) -> Optional[str]:
        """Analyze CSV data to provide specific insights"""
        try:
            content = csv_doc.get('content', '')
            lines = content.strip().split('\n')
            
            if len(lines) < 2:
                return None
            
            header = [col.strip() for col in lines[0].split(',')]
            rows = []
            
            for line in lines[1:]:
                row_data = [col.strip() for col in line.split(',')]
                if len(row_data) == len(header):
                    row_dict = dict(zip(header, row_data))
                    rows.append(row_dict)
            
            if not rows:
                return None
            
            # Analyze based on question type
            if 'most people' in question or 'most employees' in question:
                if 'Employee Count' in header or 'Employees' in header:
                    count_field = 'Employee Count' if 'Employee Count' in header else 'Employees'
                    max_dept = max(rows, key=lambda x: int(x.get(count_field, 0)))
                    return f"Specifically, {max_dept.get('Department', 'this department')} has {max_dept.get(count_field)} employees."
            
            elif 'total' in question and ('budget' in question or 'employees' in question):
                if 'Budget' in header:
                    total_budget = sum(float(row.get('Budget', 0).replace('$', '').replace(',', '')) for row in rows)
                    return f"The total budget across all departments is ${total_budget:,.2f}."
                elif 'Employee Count' in header:
                    total_employees = sum(int(row.get('Employee Count', 0)) for row in rows)
                    return f"There are {total_employees} total employees across {len(rows)} departments."
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing CSV data: {e}")
            return None
    
    def _pattern_based_answer(self, question: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Fallback pattern-based answer generation"""
        question_lower = question.lower()
        
        # Look for CSV data questions
        csv_docs = [doc for doc in documents if doc.get('filename', '').endswith('.csv')]
        if csv_docs and any(word in question_lower for word in ['department', 'employee', 'budget', 'most', 'total']):
            result = self._analyze_csv_data(question, csv_docs[0])
            if result:
                return {
                    "answer": result,
                    "source": csv_docs[0].get('filename')
                }
        
        # Look for specific information in text documents
        for doc in documents:
            content = doc.get('content', '').lower()
            
            # First day / onboarding questions
            if any(phrase in question_lower for phrase in ['first day', 'meet with', 'who should i']):
                if 'hr' in content and 'orientation' in content:
                    return {
                        "answer": "On your first day, you should report to HR for orientation. They will guide you through the onboarding process and introduce you to your team.",
                        "source": doc.get('filename')
                    }
            
            # Vacation policy questions
            if 'vacation' in question_lower or 'time off' in question_lower:
                if 'vacation' in content or 'time off' in content:
                    # Try to extract specific numbers
                    days_match = re.search(r'(\d+)\s*days?', content)
                    if days_match:
                        days = days_match.group(1)
                        return {
                            "answer": f"According to the policy, you are entitled to {days} days of vacation time. Please check the complete policy document for details on how to request time off.",
                            "source": doc.get('filename')
                        }
        
        return None
    
    def _determine_source_document(self, question: str, documents: List[Dict[str, Any]]) -> Optional[str]:
        """Determine which document is most likely to contain the answer"""
        question_lower = question.lower()
        
        # Prioritize based on question type
        if any(word in question_lower for word in ['department', 'employee', 'budget', 'most', 'total']):
            csv_docs = [doc for doc in documents if doc.get('filename', '').endswith('.csv')]
            if csv_docs:
                return csv_docs[0].get('filename')
        
        if any(word in question_lower for word in ['first day', 'onboarding', 'new employee']):
            onboarding_docs = [doc for doc in documents if 'onboarding' in doc.get('filename', '').lower()]
            if onboarding_docs:
                return onboarding_docs[0].get('filename')
        
        if any(word in question_lower for word in ['vacation', 'policy', 'time off']):
            policy_docs = [doc for doc in documents if any(word in doc.get('filename', '').lower() 
                          for word in ['policy', 'vacation'])]
            if policy_docs:
                return policy_docs[0].get('filename')
        
        # Return the first document as fallback
        return documents[0].get('filename') if documents else None
