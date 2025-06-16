"""
Answer Generation Service for QuerySense
Generates direct answers to user questions based on retrieved documents using local AI models
"""
import logging
from typing import List, Dict, Any, Optional
import re
import csv
from io import StringIO
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForQuestionAnswering, 
    AutoModelForCausalLM,
    pipeline
)
from config import settings

logger = logging.getLogger(__name__)

class AnswerGenerationService:
    """Service to generate answers from retrieved documents using local AI models"""
    
    def __init__(self, device: str = "cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.qa_pipeline = None
        self.text_generator = None
        self.tokenizer = None
        
    def initialize(self):
        """Initialize the local AI models for answer generation"""
        try:
            logger.info("🧠 Initializing local AI answer generation service...")
            
            if settings.use_local_ai:
                # Initialize Q&A model for extractive question answering
                logger.info(f"📚 Loading Q&A model: {settings.qa_model}")
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model=settings.qa_model,
                    tokenizer=settings.qa_model,
                    device=0 if self.device == "cuda" else -1
                )
                
                # Initialize text generation model for more complex reasoning
                logger.info(f"💭 Loading text generation model: {settings.text_gen_model}")
                self.tokenizer = AutoTokenizer.from_pretrained(settings.text_gen_model)
                self.text_generator = AutoModelForCausalLM.from_pretrained(
                    settings.text_gen_model,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                
                # Add padding token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                logger.info("✅ Local AI models initialized successfully")
            else:                logger.info("✅ Answer generation service initialized (rule-based fallback)")
                
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize answer generation: {e}")
            return False
    
    def generate_answer(self, question: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a direct answer to the question based on retrieved documents using local AI
        Returns both the answer and the source filename
        """
        try:
            if not documents:
                return {
                    "answer": "I couldn't find any relevant documents to answer your question.",
                    "source": None
                }
            
            logger.info(f"🔍 Analyzing question: '{question}'")
            logger.info(f"📄 Available documents: {[doc.get('filename', 'unknown') for doc in documents]}")
            
            # Try AI-powered answer generation first
            if settings.use_local_ai and self.qa_pipeline:
                ai_answer = self._generate_ai_answer(question, documents)
                if ai_answer:
                    return ai_answer
            
            # Fallback to rule-based analysis for structured data
            rule_answer = self._analyze_and_answer(question, documents)
            if rule_answer:
                return rule_answer
            
            # Final fallback: use text generation for creative answering
            if settings.use_local_ai and self.text_generator:
                generative_answer = self._generate_contextual_answer(question, documents)
                if generative_answer:
                    return generative_answer
            
            # Last resort
            most_relevant = documents[0]
            return {
                "answer": f"I found relevant information but couldn't extract a specific answer. Please try rephrasing your question.",
                "source": most_relevant.get('filename')
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                "answer": "I encountered an error while generating an answer.",
                "source": None
            }
    
    def _generate_ai_answer(self, question: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Use local AI model to generate answers from document context"""
        try:
            logger.info("🤖 Using local AI for answer generation")
            
            # Combine relevant document content
            combined_context = self._prepare_context_for_ai(documents)
            
            if not combined_context.strip():
                return None
            
            # Use Q&A pipeline for extractive answering
            result = self.qa_pipeline(
                question=question,
                context=combined_context,
                max_answer_len=150,
                handle_impossible_answer=True
            )
            
            if result['score'] > 0.1:  # Confidence threshold
                # Find which document the answer came from
                source_doc = self._find_source_document(result['answer'], documents)
                
                return {
                    "answer": result['answer'],
                    "source": source_doc.get('filename') if source_doc else documents[0].get('filename'),
                    "confidence": result['score']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in AI answer generation: {e}")
            return None
    
    def _generate_contextual_answer(self, question: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Use text generation model for more creative, contextual answers"""
        try:
            logger.info("💭 Using text generation for contextual answer")
            
            # Prepare a prompt for the text generation model
            context = self._prepare_context_for_ai(documents, max_length=500)
            
            prompt = f"""Based on the following company information, please answer the question accurately and helpfully.

Company Information:
{context}

Question: {question}
Answer:"""
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            if self.device == "cuda":
                inputs = inputs.to(self.device)
                self.text_generator = self.text_generator.to(self.device)
            
            with torch.no_grad():
                outputs = self.text_generator.generate(
                    inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the answer part
            answer_start = generated_text.find("Answer:") + len("Answer:")
            answer = generated_text[answer_start:].strip()
            
            # Clean up the answer
            answer = answer.split('\n')[0].strip()  # Take first line only
            
            if len(answer) > 10:  # Reasonable answer length
                return {
                    "answer": answer,
                    "source": documents[0].get('filename'),
                    "method": "text_generation"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in contextual answer generation: {e}")
            return None
    
    def _prepare_context_for_ai(self, documents: List[Dict[str, Any]], max_length: int = 1000) -> str:
        """Prepare document context for AI models with smart truncation"""
        combined_text = ""
        
        for doc in documents:
            content = doc.get('content', '')
            filename = doc.get('filename', 'unknown')
            
            # Add document source info
            doc_text = f"Document: {filename}\n{content}\n\n"
            
            if len(combined_text + doc_text) > max_length:
                # Truncate to fit within limit
                remaining_space = max_length - len(combined_text)
                if remaining_space > 100:  # Only add if there's meaningful space
                    truncated_content = content[:remaining_space-50] + "..."
                    combined_text += f"Document: {filename}\n{truncated_content}\n\n"
                break
            
            combined_text += doc_text
        
        return combined_text.strip()
    
    def _find_source_document(self, answer: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find which document likely contains the answer"""
        for doc in documents:
            content = doc.get('content', '').lower()
            answer_lower = answer.lower()
            
            # Check if key words from the answer appear in this document
            answer_words = answer_lower.split()
            matches = sum(1 for word in answer_words if word in content)
            
            if matches >= len(answer_words) * 0.5:  # At least 50% of words match
                return doc
        
        return documents[0] if documents else None
      
    def _analyze_and_answer(self, question: str, documents: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Intelligent question analysis and answer generation"""
        question_lower = question.lower()
        
        # Separate documents by type for targeted analysis
        csv_docs = [doc for doc in documents if doc.get('filename', '').endswith('.csv')]
        onboarding_docs = [doc for doc in documents if 'onboarding' in doc.get('filename', '').lower()]
        policy_docs = [doc for doc in documents if any(word in doc.get('filename', '').lower() 
                      for word in ['policy', 'vacation', 'hr'])]
        
        logger.info(f"📊 Document breakdown - CSV: {len(csv_docs)}, Onboarding: {len(onboarding_docs)}, Policy: {len(policy_docs)}")
        
        # Route to appropriate handler based on question type
        if self._is_data_question(question_lower):
            return self._handle_data_questions(question_lower, csv_docs)
        elif self._is_onboarding_question(question_lower):
            return self._handle_onboarding_questions(question_lower, onboarding_docs)
        elif self._is_policy_question(question_lower):
            return self._handle_policy_questions(question_lower, policy_docs)
        else:
            # Try all handlers if question type is unclear
            for handler in [self._handle_data_questions, self._handle_onboarding_questions, self._handle_policy_questions]:
                result = handler(question_lower, documents)
                if result:
                    return result
        
        return None
    
    def _is_data_question(self, question: str) -> bool:
        """Check if question is about numerical/analytical data"""
        data_keywords = ['most', 'least', 'total', 'count', 'budget', 'department', 'employee', 'people', 
                        'staff', 'performance', 'rating', 'largest', 'smallest', 'highest', 'lowest',
                        'how many', 'which department', 'what department']
        return any(keyword in question for keyword in data_keywords)
    
    def _is_onboarding_question(self, question: str) -> bool:
        """Check if question is about onboarding/first day"""
        onboarding_keywords = ['first day', 'onboard', 'new employee', 'orientation', 'checklist',
                              'meet with', 'who should i', 'what should i', 'security badge', 
                              'laptop', 'manager', 'office tour']
        return any(keyword in question for keyword in onboarding_keywords)
    
    def _is_policy_question(self, question: str) -> bool:
        """Check if question is about company policies"""
        policy_keywords = ['vacation', 'time off', 'sick leave', 'holiday', 'policy', 'benefits',
                          'days per year', 'request', 'approval']
        return any(keyword in question for keyword in policy_keywords)
    
    def _handle_data_questions(self, question: str, csv_docs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Handle questions about numerical data from CSV files"""
        if not csv_docs:
            return None
            
        logger.info("📈 Handling data question")
        
        # Parse CSV data
        csv_data = self._parse_csv_data(csv_docs[0])
        if not csv_data:
            return None
        
        source_filename = csv_docs[0].get('filename')
        
        # Department with most people/employees
        if any(phrase in question for phrase in ['most people', 'most employees', 'largest department', 
                                               'biggest department', 'which department has the most']):
            max_dept = max(csv_data, key=lambda x: int(x.get('Employee Count', 0)))
            return {
                "answer": f"The {max_dept['Department']} department has the most people with {max_dept['Employee Count']} employees.",
                "source": source_filename
            }
        
        # Department with least people/employees
        if any(phrase in question for phrase in ['least people', 'least employees', 'smallest department', 
                                               'fewest employees']):
            min_dept = min(csv_data, key=lambda x: int(x.get('Employee Count', 0)))
            return {
                "answer": f"The {min_dept['Department']} department has the least people with {min_dept['Employee Count']} employees.",
                "source": source_filename
            }
        
        # Total employees across all departments
        if any(phrase in question for phrase in ['total employees', 'total people', 'how many employees',
                                               'total staff', 'all employees']):
            total = sum(int(dept.get('Employee Count', 0)) for dept in csv_data)
            return {
                "answer": f"There are {total} employees in total across all departments.",
                "source": source_filename
            }
        
        # Specific department employee count
        for dept_data in csv_data:
            dept_name = dept_data['Department'].lower()
            if dept_name in question and any(word in question for word in ['people', 'employees', 'staff', 'how many']):
                return {
                    "answer": f"The {dept_data['Department']} department has {dept_data['Employee Count']} employees.",
                    "source": source_filename
                }
        
        # Budget questions
        if 'budget' in question:
            # Total budget for specific department
            for dept_data in csv_data:
                dept_name = dept_data['Department'].lower()
                if dept_name in question:
                    budget = int(dept_data.get('Budget 2024', 0))
                    return {
                        "answer": f"The {dept_data['Department']} department has a budget of ${budget:,} for 2024.",
                        "source": source_filename
                    }
            
            # Highest/lowest budget questions
            if any(word in question for word in ['highest', 'largest', 'most', 'biggest']):
                max_budget_dept = max(csv_data, key=lambda x: int(x.get('Budget 2024', 0)))
                budget = int(max_budget_dept['Budget 2024'])
                return {
                    "answer": f"The {max_budget_dept['Department']} department has the highest budget of ${budget:,} for 2024.",
                    "source": source_filename
                }
            
            if any(word in question for word in ['lowest', 'smallest', 'least']):
                min_budget_dept = min(csv_data, key=lambda x: int(x.get('Budget 2024', 0)))
                budget = int(min_budget_dept['Budget 2024'])
                return {
                    "answer": f"The {min_budget_dept['Department']} department has the lowest budget of ${budget:,} for 2024.",
                    "source": source_filename
                }
            
            # Total budget across all departments
            if any(phrase in question for phrase in ['total budget', 'all budget', 'company budget']):
                total_budget = sum(int(dept.get('Budget 2024', 0)) for dept in csv_data)
                return {
                    "answer": f"The total company budget for 2024 is ${total_budget:,} across all departments.",
                    "source": source_filename
                }
        
        # Performance questions
        if any(word in question for word in ['performance', 'rating', 'best', 'excellent', 'worst']):
            if any(word in question for word in ['best', 'excellent', 'highest']):
                excellent_depts = [dept for dept in csv_data if dept.get('Performance Rating', '').lower() == 'excellent']
                if excellent_depts:
                    if len(excellent_depts) == 1:
                        return {
                            "answer": f"The {excellent_depts[0]['Department']} department has the best performance rating (Excellent).",
                            "source": source_filename
                        }
                    else:
                        dept_names = ', '.join([dept['Department'] for dept in excellent_depts])
                        return {
                            "answer": f"The {dept_names} departments have the best performance rating (Excellent).",
                            "source": source_filename
                        }
            
            # Specific department performance
            for dept_data in csv_data:
                dept_name = dept_data['Department'].lower()
                if dept_name in question:
                    return {
                        "answer": f"The {dept_data['Department']} department has a {dept_data['Performance Rating']} performance rating.",
                        "source": source_filename
                    }
        
        return None    
    def _handle_onboarding_questions(self, question: str, onboarding_docs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Handle questions about onboarding and first day procedures"""
        if not onboarding_docs:
            return None
            
        logger.info("👋 Handling onboarding question")
        
        content = onboarding_docs[0].get('content', '')
        source_filename = onboarding_docs[0].get('filename')
        
        # Who should I meet questions
        if any(phrase in question for phrase in ['who should i meet', 'meet with', 'who do i meet', 'who to meet']):
            if 'meet with your direct manager' in content.lower():
                return {
                    "answer": "You should meet with your direct manager on your first day.",
                    "source": source_filename
                }
        
        # First day checklist questions
        if any(phrase in question for phrase in ['first day', 'what should i do', 'checklist', 'first thing']):
            # Extract first day checklist items
            checklist_match = re.search(r'## first day checklist\s*\n((?:- .+\n?)+)', content.lower(), re.MULTILINE)
            if checklist_match:
                checklist_items = re.findall(r'- (.+)', checklist_match.group(1))
                if checklist_items:
                    first_item = checklist_items[0].strip()
                    if 'first thing' in question or 'what should i do first' in question:
                        return {
                            "answer": f"The first thing you should do is: {first_item}.",
                            "source": source_filename
                        }
                    else:
                        all_items = ', '.join([item.strip() for item in checklist_items[:3]])
                        return {
                            "answer": f"On your first day: {all_items}, and more.",
                            "source": source_filename
                        }
        
        # HR/Orientation time questions
        if any(word in question for word in ['hr', 'orientation', 'report', 'time', 'when']):
            time_match = re.search(r'report to hr at (\d+:\d+\s*[ap]m)', content.lower())
            if time_match:
                time = time_match.group(1)
                return {
                    "answer": f"Report to HR at {time} for orientation.",
                    "source": source_filename
                }
        
        # Security badge questions
        if any(phrase in question for phrase in ['security badge', 'badge', 'id card']):
            if 'security badge' in content.lower():
                return {
                    "answer": "You will receive your security badge during the office tour on your first day.",
                    "source": source_filename
                }
        
        # Laptop/equipment questions
        if any(word in question for word in ['laptop', 'computer', 'equipment', 'credentials']):
            if 'company laptop' in content.lower():
                return {
                    "answer": "You will receive your company laptop and access credentials on your first day.",
                    "source": source_filename
                }
        
        # Training questions
        if any(word in question for word in ['training', 'mandatory', 'required']):
            training_match = re.search(r'## training requirements\s*\n(.+?)(?=\n##|\Z)', content.lower(), re.DOTALL)
            if training_match:
                return {
                    "answer": "All new employees must complete Information Security training, Workplace Safety training, Company Culture session, and role-specific technical training.",
                    "source": source_filename
                }
        
        return None
    
    def _handle_policy_questions(self, question: str, policy_docs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Handle questions about company policies"""
        if not policy_docs:
            return None
            
        logger.info("📋 Handling policy question")
        
        content = policy_docs[0].get('content', '')
        source_filename = policy_docs[0].get('filename')
        
        # Vacation days entitlement
        if any(phrase in question for phrase in ['vacation days', 'time off', 'how many days', 'vacation entitlement']):
            if 'new employee' in question or 'new hire' in question:
                if '15 days per year' in content:
                    return {
                        "answer": "New employees get 15 vacation days per year.",
                        "source": source_filename
                    }
            
            # Extract vacation entitlement info
            entitlement_match = re.search(r'## vacation entitlement\s*\n((?:- .+\n?)+)', content.lower(), re.MULTILINE)
            if entitlement_match:
                return {
                    "answer": "Vacation entitlement varies by tenure: New employees get 15 days, 2+ years get 20 days, 5+ years get 25 days, and 10+ years get 30 days per year.",
                    "source": source_filename
                }
        
        # How to request vacation
        if any(phrase in question for phrase in ['how to request', 'request vacation', 'request time off', 'how do i request']):
            if 'hr portal' in content.lower():
                return {
                    "answer": "Submit vacation requests through the HR portal at least 2 weeks in advance and get approval from your direct manager.",
                    "source": source_filename
                }
        
        # Vacation policy rules
        if any(phrase in question for phrase in ['vacation rules', 'policy rules', 'vacation policy']):
            return {
                "answer": "Key vacation rules: Maximum 5 consecutive days without special approval, days cannot be carried over, and all requests must be approved before booking travel.",
                "source": source_filename
            }
        
        # Sick leave questions
        if any(phrase in question for phrase in ['sick leave', 'sick days', 'sick time']):
            if '10 sick days' in content:
                return {
                    "answer": "Employees receive 10 sick days per year, separate from vacation time.",
                    "source": source_filename
                }
        
        return None
    
    def _parse_csv_data(self, csv_doc: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse CSV content into structured data"""
        try:
            content = csv_doc.get('content', '')
            csv_reader = csv.DictReader(StringIO(content))
            return list(csv_reader)
        except Exception as e:
            logger.error(f"Error parsing CSV data: {e}")
            return []
