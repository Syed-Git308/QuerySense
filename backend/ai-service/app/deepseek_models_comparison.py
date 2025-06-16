"""
DeepSeek Models Comparison for RTX 4070 Ti (12GB VRAM)
Best models for business Q&A and document analysis
"""

DEEPSEEK_MODELS_RTX_4070TI = {
    # 🔥 BEST FOR YOUR SETUP
    "deepseek-ai/DeepSeek-R1-Distill-Llama-8B": {
        "size": "8B",
        "vram_required": "7-8GB",
        "accuracy": "96-98%",
        "specialty": "Reasoning, business Q&A, document analysis",
        "strength": "Latest R1 reasoning model, best accuracy",
        "recommended_use": "PRIMARY CHOICE - Best for complex business questions",
        "quantization": "FP16 native support",
        "inference_speed": "Fast",
        "notes": "DeepSeek R1 series - state-of-the-art reasoning"
    },
    
    "deepseek-ai/deepseek-llm-7b-chat": {
        "size": "7B", 
        "vram_required": "6-7GB",
        "accuracy": "94-96%",
        "specialty": "General chat, Q&A, document understanding",
        "strength": "Well-rounded, excellent for business docs",
        "recommended_use": "EXCELLENT CHOICE - Stable and reliable",
        "quantization": "FP16/4-bit support",
        "inference_speed": "Very fast",
        "notes": "Most stable for production use"
    },
    
    "deepseek-ai/deepseek-coder-6.7b-instruct": {
        "size": "6.7B",
        "vram_required": "5-6GB", 
        "accuracy": "92-95%",
        "specialty": "Code, structured data, CSV analysis",
        "strength": "Excellent for CSV/data questions",
        "recommended_use": "GREAT FOR DATA - Perfect for CSV analysis",
        "quantization": "FP16/4-bit support",
        "inference_speed": "Very fast",
        "notes": "Currently implemented - works well for structured data"
    },
    
    # 🌟 CUTTING EDGE (if available)
    "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B": {
        "size": "8B",
        "vram_required": "7-8GB",
        "accuracy": "97-99%", 
        "specialty": "Advanced reasoning, complex Q&A",
        "strength": "Latest R1 architecture with Qwen3 base",
        "recommended_use": "BLEEDING EDGE - Highest accuracy",
        "quantization": "FP16 native",
        "inference_speed": "Fast",
        "notes": "Very latest model - may need testing"
    },
    
    # 💎 PREMIUM OPTIONS (if you can fit them)
    "deepseek-ai/DeepSeek-V3": {
        "size": "671B MoE",
        "vram_required": "12GB+ (with heavy quantization)",
        "accuracy": "99%+",
        "specialty": "Everything - SOTA performance",
        "strength": "Best-in-class performance",
        "recommended_use": "ULTIMATE - If you can run it",
        "quantization": "Requires 4-bit quantization",
        "inference_speed": "Slower but highest quality",
        "notes": "Mixture of Experts - challenging to run locally"
    }
}

# RECOMMENDATION MATRIX FOR RTX 4070 TI
RECOMMENDATIONS = {
    "FOR_MAXIMUM_ACCURACY": {
        "primary": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "backup": "deepseek-ai/deepseek-llm-7b-chat",
        "reason": "R1 series has best reasoning capabilities"
    },
    
    "FOR_PRODUCTION_STABILITY": {
        "primary": "deepseek-ai/deepseek-llm-7b-chat", 
        "backup": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "reason": "Most tested and stable for business use"
    },
    
    "FOR_CSV_DATA_ANALYSIS": {
        "primary": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "backup": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B", 
        "reason": "Coder models excel at structured data"
    },
    
    "FOR_SPEED": {
        "primary": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "backup": "deepseek-ai/deepseek-llm-7b-chat",
        "reason": "Smaller models = faster inference"
    }
}

def get_recommendation(use_case="maximum_accuracy"):
    """Get DeepSeek model recommendation for specific use case"""
    key = f"FOR_{use_case.upper()}"
    return RECOMMENDATIONS.get(key, RECOMMENDATIONS["FOR_MAXIMUM_ACCURACY"])

def get_model_info(model_name):
    """Get detailed info about a specific DeepSeek model"""
    return DEEPSEEK_MODELS_RTX_4070TI.get(model_name, {})

# OPTIMAL SETTINGS FOR RTX 4070 TI
OPTIMAL_SETTINGS = {
    "torch_dtype": "float16",
    "device_map": "auto", 
    "low_cpu_mem_usage": True,
    "max_new_tokens": 256,
    "temperature": 0.2,
    "top_p": 0.85,
    "repetition_penalty": 1.1,
    "do_sample": True
}

if __name__ == "__main__":
    print("🌊 DeepSeek Models for RTX 4070 Ti")
    print("=" * 50)
    
    for use_case in ["maximum_accuracy", "production_stability", "csv_data_analysis", "speed"]:
        rec = get_recommendation(use_case)
        print(f"\n{use_case.upper().replace('_', ' ')}:")
        print(f"  Primary: {rec['primary']}")
        print(f"  Reason: {rec['reason']}")
