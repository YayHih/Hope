#!/bin/bash

# Hope Platform - Quick Setup Script
# This script sets up the development environment

set -e

echo "================================================"
echo "Hope Platform - Development Setup"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment files
echo ""
echo "📝 Creating environment files..."

# Backend .env
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
else
    echo "  backend/.env already exists"
fi

# Scraper .env
if [ ! -f scraper/.env ]; then
    cp scraper/.env.example scraper/.env
    echo "✓ Created scraper/.env"
else
    echo "  scraper/.env already exists"
fi

# Start Docker services
echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if services are running
echo ""
echo "✅ Services Status:"
docker-compose ps

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Health:      http://localhost:8000/health"
echo ""
echo "Next steps:"
echo "1. Test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "2. Run the scraper to populate data:"
echo "   cd scraper"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo "   python -m scraper.main"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "To stop services:"
echo "   docker-compose down"
echo ""
