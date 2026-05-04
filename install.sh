#!/bin/bash
set -e
echo "=== Installing ai-market-analysis-bot ==="

if ! command -v docker &> /dev/null; then echo "Docker is required."; exit 1; fi

echo "Starting Ollama service..."
docker compose up -d ollama
sleep 5

echo "Pulling llama3 model (this may take a while on first run)..."
docker compose exec ollama ollama pull llama3 2>/dev/null || echo "Model pull initiated"

echo "Starting all services..."
docker compose up -d

echo "=== ai-market-analysis-bot is running ==="
echo "Open http://localhost:8515"
