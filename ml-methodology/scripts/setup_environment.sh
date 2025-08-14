#!/bin/bash

# FinRisk Environment Setup Script

echo "🚀 Setting up FinRisk environment..."

# Check if Python 3.9+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/raw data/processed data/synthetic logs models

# Copy existing data files if they exist
if [ -d "../Data" ]; then
    echo "📋 Copying existing data files..."
    cp ../Data/*.csv data/raw/ 2>/dev/null || true
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOF
# FinRisk Environment Variables
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://finrisk_user:finrisk_password@localhost:5432/finrisk_db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RATE_LIMIT=1000

# Security
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION=3600

# Monitoring
MLFLOW_TRACKING_URI=http://localhost:5000
PROMETHEUS_ENABLED=true

# External Services
CREDIT_BUREAU_API_KEY=your-api-key
FRAUD_SERVICE_API_KEY=your-api-key
EOF
    echo "✅ .env file created. Please update with your actual values."
fi

# Set up pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pip install pre-commit
pre-commit install

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✅ Environment setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your actual configuration"
echo "2. Run 'source venv/bin/activate' to activate the environment"
echo "3. Run 'python scripts/train_models.py' to train initial models"
echo "4. Run 'uvicorn src.api.main:app --reload' to start the API server"
echo "5. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "🐳 For Docker deployment:"
echo "1. Run 'docker-compose up -d' to start all services"
echo "2. Visit http://localhost:8000 for the API"
echo "3. Visit http://localhost:3000 for Grafana dashboard"
