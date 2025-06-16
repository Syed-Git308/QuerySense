#!/usr/bin/env python3
"""
QuerySense Phase 2 Setup Script
Automatically installs and configures the AI service
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_gpu():
    """Check NVIDIA GPU availability"""
    try:
        result = subprocess.run("nvidia-smi", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detected")
            print("🎮 RTX 4070 Ti ready for AI acceleration!")
            return True
    except:
        pass
    print("⚠️  NVIDIA GPU not detected, using CPU fallback")
    return False

def install_dependencies():
    """Install Python dependencies"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Install PyTorch with CUDA support first
    print("🔥 Installing PyTorch with CUDA support...")
    torch_command = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    if not run_command(torch_command, "Installing PyTorch with CUDA"):
        return False
    
    # Install other requirements
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def test_installation():
    """Test if everything is installed correctly"""
    test_script = '''
import torch
import sentence_transformers
import sqlalchemy
import fastapi
import numpy as np

print("✅ All imports successful")
print(f"🔥 PyTorch CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name()}")
print(f"🧠 Sentence Transformers: {sentence_transformers.__version__}")
'''
    
    try:
        result = subprocess.run([sys.executable, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print("✅ Installation test passed")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Installation test failed:")
        print(e.stderr)
        return False

def setup_database_info():
    """Display database setup instructions"""
    print("""
🗄️  DATABASE SETUP REQUIRED:

1. Install PostgreSQL 15+ if not already installed
2. Install pgvector extension
3. Run the setup script:

   psql -U postgres -f setup_database.sql

Or manually create:
   CREATE DATABASE querysense_ai;
   CREATE USER querysense WITH PASSWORD 'querysense123';
   GRANT ALL PRIVILEGES ON DATABASE querysense_ai TO querysense;
   \\c querysense_ai
   CREATE EXTENSION vector;
""")

def main():
    """Main setup function"""
    print("🚀 QuerySense Phase 2: AI Service Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python():
        sys.exit(1)
    
    gpu_available = check_gpu()
    
    # Install dependencies
    print("\n📦 Installing Dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Test installation
    print("\n🧪 Testing Installation...")
    if not test_installation():
        print("❌ Installation test failed")
        sys.exit(1)
    
    # Database setup info
    setup_database_info()
    
    print("""
🎉 PHASE 2 SETUP COMPLETE!

Next steps:
1. Set up PostgreSQL database (see instructions above)
2. Start the AI service: python main.py
3. Service will be available at: http://localhost:8001

Your RTX 4070 Ti is ready to power intelligent semantic search! 🔥
""")

if __name__ == "__main__":
    main()
