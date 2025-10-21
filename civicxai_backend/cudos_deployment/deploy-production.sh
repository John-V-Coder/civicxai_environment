# =====================================================
# deploy-production.sh - Production Deployment
# =====================================================
#!/bin/bash

set -e

echo "=================================================="
echo "CivicXAI Production Deployment (with Cudos Node)"
echo "=================================================="

# Production checks
if [ ! -f .env ]; then
    echo ".env file not found!"
    exit 1
fi

# Validate critical environment variables
source .env

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ANTHROPIC_API_KEY not set!"
    exit 1
fi

if [ -z "$GATEWAY_AGENT_SEED" ] || [ "$GATEWAY_AGENT_SEED" = "your_unique_gateway_seed_here_change_this" ]; then
    echo "Please set a unique GATEWAY_AGENT_SEED!"
    exit 1
fi

if [ -z "$PROVIDER_AGENT_SEED" ] || [ "$PROVIDER_AGENT_SEED" = "your_unique_provider_seed_here_change_this" ]; then
    echo "Please set a unique PROVIDER_AGENT_SEED!"
    exit 1
fi

echo "Environment validation passed"

# Deploy with production profile (includes Cudos node)
echo "Starting production deployment..."
docker-compose --profile production up -d

echo ""
echo "=================================================="
echo "Production Deployment Complete!"
echo "=================================================="
echo "All services running including Cudos full node"
echo "Monitor with: docker-compose logs -f"
echo "=================================================="
