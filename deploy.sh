#!/bin/bash

# FinRisk Production Deployment Script
set -e

echo "🚀 Starting FinRisk Production Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.production.example .env
    print_warning "Please update .env with your production values before continuing."
    exit 1
fi

# Load environment variables
print_status "Loading environment variables..."
source .env

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs models data

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Run tests
print_status "Running production tests..."
python -m pytest tests/ -v --tb=short

# Build Docker image (if using Docker)
if command -v docker &> /dev/null; then
    print_status "Building Docker image..."
    docker build -t finrisk:latest .
    
    print_status "Docker image built successfully!"
    print_status "To run with Docker:"
    echo "  docker run -p 8000:8000 --env-file .env finrisk:latest"
fi

# Start services with Docker Compose (if available)
if command -v docker-compose &> /dev/null; then
    print_status "Starting services with Docker Compose..."
    docker-compose -f docker-compose.prod.yml up -d
    
    print_status "Services started successfully!"
    print_status "API will be available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health Check: http://localhost:8000/health"
else
    print_warning "Docker Compose not found. Starting application directly..."
    
    # Start the application
    print_status "Starting FinRisk API..."
    gunicorn src.api.main:app \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --timeout 120 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info
fi

print_status "🎉 FinRisk Production Deployment Complete!"
print_status "📊 Monitor logs: tail -f logs/finrisk.log"
print_status "🔍 Health check: curl http://localhost:8000/health"
