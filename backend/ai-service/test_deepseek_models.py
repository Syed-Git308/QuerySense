"""
DeepSeek Model Testing and Benchmarking for RTX 4070 Ti
Test different DeepSeek models with your business documents
"""
import sys
import os
import time
import torch
import logging
import numpy as np
from typing import Dict, List
from sqlalchemy.orm import Session

# Add the app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.enhanced_deepseek_generator import EnhancedDeepSeekGenerator
from app.deepseek_models_comparison import DEEPSEEK_MODELS_RTX_4070TI

# Try to import database
try:
    from app.database import get_db, Document
    USE_DATABASE = True
except:
    try:
        from app.database_simple import SessionLocal, Document
        USE_DATABASE = True
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
    except:
        USE_DATABASE = False
        Document = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test which DeepSeek models can be loaded on RTX 4070 Ti"""
    
    print("🌊 DeepSeek Model Loading Test for RTX 4070 Ti")
    print("=" * 60)
    
    if not torch.cuda.is_available():
        print("❌ CUDA not available. Please ensure you have NVIDIA drivers and PyTorch with CUDA.")
        return
    
    print(f"🚀 GPU: {torch.cuda.get_device_name(0)}")
    print(f"💾 Total VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    print()
    
    # Test models in order of preference
    test_models = [
        "deepseek-ai/deepseek-coder-6.7b-instruct",  # Currently working
        "deepseek-ai/deepseek-llm-7b-chat",           # Most stable
        "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",  # Latest R1 (if available)
    ]
    
    results = {}
    
    for model_name in test_models:
        print(f"\\n🔥 Testing {model_name}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Initialize generator
            generator = EnhancedDeepSeekGenerator(preferred_model=model_name)
            
            # Test loading
            generator.initialize()
            
            load_time = time.time() - start_time
            
            # Get model info
            info = generator.get_model_info()
            
            results[model_name] = {
                "status": "✅ SUCCESS",
                "load_time": f"{load_time:.1f}s",
                "vram_usage": f"{info.get('vram_usage_gb', 0):.1f}GB",
                "accuracy": info.get('accuracy', 'Unknown'),
                "notes": "Ready for use"
            }
            
            print(f"✅ Loaded successfully in {load_time:.1f}s")
            print(f"💾 VRAM Usage: {info.get('vram_usage_gb', 0):.1f}GB")
            print(f"🎯 Expected Accuracy: {info.get('accuracy', 'Unknown')}")
            
            # Cleanup
            del generator
            torch.cuda.empty_cache()
            
        except Exception as e:
            results[model_name] = {
                "status": "❌ FAILED",
                "load_time": "N/A",
                "vram_usage": "N/A", 
                "accuracy": "N/A",
                "notes": str(e)
            }
            
            print(f"❌ Failed: {e}")
            torch.cuda.empty_cache()
    
    # Print summary
    print("\\n" + "=" * 60)
    print("📊 LOADING TEST SUMMARY")
    print("=" * 60)
    
    for model, result in results.items():
        model_short = model.split('/')[-1]
        print(f"\\n{model_short}:")
        print(f"  Status: {result['status']}")
        print(f"  Load Time: {result['load_time']}")
        print(f"  VRAM: {result['vram_usage']}")
        print(f"  Accuracy: {result['accuracy']}")
        if result['notes'] != "Ready for use":
            print(f"  Error: {result['notes']}")
    
    return results

def simple_document_search(query: str) -> List[Dict]:
    """Simple document search for testing"""
    if not USE_DATABASE:
        # Mock documents for testing
        return [
            {
                "content": "Employees are entitled to 25 vacation days per year. New employees receive prorated vacation days based on their start date.",
                "filename": "vacation-policy.txt",
                "similarity": 0.9
            },
            {
                "content": "Department,Employee Count\nEngineering,150\nSales,75\nMarketing,45\nHR,25\nFinance,30",
                "filename": "company-data.csv", 
                "similarity": 0.8
            }
        ]
    
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)
        
        # Get all documents
        documents = db.query(Document).all()
        
        # Simple keyword matching for testing
        results = []
        for doc in documents:
            content = doc.content.lower()
            query_lower = query.lower()
            
            # Simple scoring based on keyword matches
            score = sum(1 for word in query_lower.split() if word in content and len(word) > 3)
            
            if score > 0:
                results.append({
                    "content": doc.content,
                    "filename": doc.filename,
                    "similarity": min(0.9, score * 0.2)
                })
        
        db.close()
        return results[:2]  # Return top 2
        
    except Exception as e:
        logger.error(f"Database search failed: {e}")
        # Return mock data as fallback
        return simple_document_search(query) if USE_DATABASE else []

def test_model_accuracy():
    """Test answer accuracy with sample business questions"""
    
    print("\\n🎯 DeepSeek Accuracy Test")
    print("=" * 60)
    
    # Test questions based on your documents
    test_questions = [
        "How many vacation days do employees get per year?",
        "Which department has the most employees?", 
        "What is the vacation policy for new employees?",
        "How many employees work in the Engineering department?",
        "What are the company holidays mentioned in the policy?"
    ]
    
    # Initialize with best available model
    try:
        generator = EnhancedDeepSeekGenerator(use_case="maximum_accuracy")
        generator.initialize()
        
        print(f"🤖 Testing with: {generator.model_name}")
        print(f"🎯 Expected Accuracy: {generator.model_info.get('accuracy', 'Unknown')}")
        print()
        
        for i, question in enumerate(test_questions, 1):
            print(f"\\n❓ Question {i}: {question}")
            print("-" * 40)
            
            try:
                # Search for relevant documents
                results = simple_document_search(question)
                
                if not results:
                    print("⚠️ No documents found for this question")
                    continue
                
                # Generate answer
                start_time = time.time()
                response = generator.generate_answer(question, results)
                response_time = time.time() - start_time
                
                print(f"💬 Answer: {response['answer']}")
                print(f"🎯 Confidence: {response['confidence']:.1%}")
                print(f"📄 Source: {response.get('source', 'Unknown')}")
                print(f"⏱️ Response Time: {response_time:.2f}s")
                print(f"🤖 Model: {response.get('model_used', 'Unknown')}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Cleanup
        del generator
        torch.cuda.empty_cache()
        
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")

def benchmark_models():
    """Benchmark different models for speed and quality"""
    
    print("\\n⚡ DeepSeek Speed Benchmark")
    print("=" * 60)
    
    models_to_test = [
        "deepseek-ai/deepseek-coder-6.7b-instruct",
        "deepseek-ai/deepseek-llm-7b-chat"
    ]
    
    test_question = "How many vacation days do employees get per year?"
    
    for model_name in models_to_test:
        print(f"\\n🔥 Benchmarking {model_name.split('/')[-1]}")
        print("-" * 40)
        
        try:
            generator = EnhancedDeepSeekGenerator(preferred_model=model_name)
            
            # Time the loading
            start_load = time.time()
            generator.initialize()
            load_time = time.time() - start_load
              # Get documents
            documents = simple_document_search(test_question)
            
            if documents:
                # Time the inference (multiple runs for average)
                times = []
                for _ in range(3):
                    start_inference = time.time()
                    response = generator.generate_answer(test_question, documents)
                    inference_time = time.time() - start_inference
                    times.append(inference_time)
                
                avg_time = sum(times) / len(times)
                
                print(f"📊 Results:")
                print(f"  Load Time: {load_time:.1f}s")
                print(f"  Avg Inference: {avg_time:.2f}s")
                print(f"  VRAM Usage: {generator.get_model_info().get('vram_usage_gb', 0):.1f}GB")
                print(f"  Sample Answer: {response['answer'][:100]}...")
            
            del generator
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"❌ Failed: {e}")

def main():
    """Run comprehensive DeepSeek testing"""
    
    print("🌊 DeepSeek Testing Suite for RTX 4070 Ti")
    print("=" * 60)
    print("This will test DeepSeek models for your business Q&A system")
    print()
    
    # Test 1: Model Loading
    loading_results = test_model_loading()
    
    # Test 2: Accuracy Testing
    test_model_accuracy()
    
    # Test 3: Speed Benchmarking  
    benchmark_models()
    
    # Final recommendations
    print("\\n" + "=" * 60)
    print("🎯 FINAL RECOMMENDATIONS FOR RTX 4070 TI")
    print("=" * 60)
    
    successful_models = [model for model, result in loading_results.items() if "SUCCESS" in result["status"]]
    
    if successful_models:
        print("\\n✅ RECOMMENDED MODELS (in order of preference):")
        
        # Sort by preference
        model_preference = [
            "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
            "deepseek-ai/deepseek-llm-7b-chat", 
            "deepseek-ai/deepseek-coder-6.7b-instruct"
        ]
        
        for model in model_preference:
            if model in successful_models:
                info = DEEPSEEK_MODELS_RTX_4070TI.get(model, {})
                model_short = model.split('/')[-1]
                print(f"\\n🥇 {model_short}")
                print(f"   Accuracy: {info.get('accuracy', 'Unknown')}")
                print(f"   VRAM: {info.get('vram_required', 'Unknown')}")
                print(f"   Best for: {info.get('recommended_use', 'General use')}")
                break
        
        print("\\n📝 NEXT STEPS:")
        print("1. Update your main.py to use Enhanced DeepSeek Generator")
        print("2. Choose your preferred model from the successful ones above")
        print("3. Test with your specific business questions")
        print("4. Monitor VRAM usage and adjust if needed")
        
    else:
        print("\\n❌ No models loaded successfully. Check your PyTorch CUDA installation.")
        print("   Try installing: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

if __name__ == "__main__":
    main()
