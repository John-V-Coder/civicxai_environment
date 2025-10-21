# =====================================================
# deploy.sh - Deployment Script
# =====================================================
#!/bin/bash

set -e

echo "=================================================="
echo "CivicXAI Cudos Deployment Script"
echo "=================================================="

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is required but not installed. Aborting." >&2; exit 1; }

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration before continuing!"
    exit 1
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads cache logs config/cudos

# Pull latest images
echo "Pulling Docker images..."
docker-compose pull

# Build services
echo "Building services..."
docker-compose build

# Start services
echo "Starting services..."
docker-compose up -d civicxai-gateway civicxai-provider

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check health
echo "Checking service health..."
curl -f http://localhost:8080/health || echo " Gateway health check failed"

# Display status
echo ""
echo "=================================================="
echo "Deployment Complete!"
echo "=================================================="
echo "Gateway API: http://localhost:8080"
echo "Gateway Agent: Port 8000"
echo "Provider Agent: Port 8001"
echo ""
echo "View logs with: docker-compose logs -f"
echo "Stop services with: docker-compose down"
echo "=================================================="

# Display agent addresses
echo ""
echo "Getting agent addresses..."
docker-compose logs civicxai-gateway | grep "agent started" || true
docker-compose logs civicxai-provider | grep "agent initialized" || true