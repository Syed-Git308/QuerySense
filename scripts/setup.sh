#!/bin/bash

# QuerySense Development Environment Setup Script

echo "🚀 Setting up QuerySense development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo "❌ Rust is not installed. Please install Rust first."
    echo "Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ All required tools are installed!"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file from template"
    echo "⚠️  Please update .env with your actual configuration values"
fi

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Install realtime service dependencies
echo "📦 Installing realtime service dependencies..."
cd backend/realtime-service && npm install && cd ../..

# Install Python dependencies for AI service
echo "📦 Installing AI service dependencies..."
cd backend/ai-service && python3 -m pip install -r requirements.txt && cd ../..

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run 'npm run dev' to start all services"
echo "3. Visit http://localhost:3000 for the frontend"
echo "4. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "📚 Available commands:"
echo "- npm run dev          # Start all services"
echo "- npm run dev:frontend # Start only frontend"
echo "- npm run dev:backend  # Start only backend"
echo "- npm run docker:down  # Stop Docker services"
