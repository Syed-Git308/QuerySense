# QuerySense Phase 2: AI Service Setup (Windows PowerShell)
# Run this script to set up the AI service on your Windows machine

Write-Host "🚀 QuerySense Phase 2: AI Service Setup" -ForegroundColor Green
Write-Host "=" * 50

# Check Python installation
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}

# Check NVIDIA GPU
Write-Host "🎮 Checking GPU..." -ForegroundColor Cyan
try {
    $nvidiaInfo = nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ NVIDIA GPU detected - RTX 4070 Ti ready!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  NVIDIA GPU not detected, will use CPU" -ForegroundColor Yellow
}

# Create virtual environment
Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Cyan
python -m venv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install PyTorch with CUDA support first
Write-Host "🔥 Installing PyTorch with CUDA support..." -ForegroundColor Cyan
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install PyTorch" -ForegroundColor Red
    exit 1
}

# Install other dependencies
Write-Host "📚 Installing other dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Test installation
Write-Host "🧪 Testing installation..." -ForegroundColor Cyan
$testScript = @"
import torch
import sentence_transformers
import fastapi
import numpy as np
print("✅ All imports successful")
print(f"🔥 PyTorch CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"🎮 GPU: {torch.cuda.get_device_name()}")
"@

$testResult = python -c $testScript
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Installation test passed!" -ForegroundColor Green
    Write-Host $testResult
} else {
    Write-Host "❌ Installation test failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 PHASE 2 AI SERVICE SETUP COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Set up PostgreSQL database:" -ForegroundColor White
Write-Host "   - Install PostgreSQL 15+ if not installed" -ForegroundColor Gray
Write-Host "   - Install pgvector extension" -ForegroundColor Gray
Write-Host "   - Run: psql -U postgres -f setup_database.sql" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the AI service:" -ForegroundColor White
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Service will be available at:" -ForegroundColor White
Write-Host "   http://localhost:8001" -ForegroundColor Gray
Write-Host ""
Write-Host "Your RTX 4070 Ti is ready to power intelligent semantic search! 🔥" -ForegroundColor Green
