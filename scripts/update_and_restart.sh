#!/bin/bash
# Update MLflow model and restart service with new Qwen API key

echo "=========================================="
echo "Updating Qwen API Key Configuration"
echo "=========================================="

# Step 1: Show current .env configuration
echo ""
echo "[1/4] Current .env configuration:"
echo "--------------------------------"
grep -E "LLM_PROVIDER|QWEN_API_KEY|OPENAI_API_KEY" ../.env | head -3

# Step 2: Rebuild MLflow model
echo ""
echo "[2/4] Rebuilding MLflow model with Qwen..."
echo "--------------------------------"
cd ..
python scripts/log_mlflow_model.py

# Step 3: Restart Docker container
echo ""
echo "[3/4] Restarting Docker container..."
echo "--------------------------------"
cd web
docker-compose down
docker-compose up -d

# Step 4: Wait and check status
echo ""
echo "[4/4] Waiting for service to start..."
echo "--------------------------------"
sleep 15

echo ""
echo "Checking service status..."
docker-compose ps

echo ""
echo "Checking environment variables..."
docker-compose exec -T ecu-assistant-api printenv | grep -E "QWEN_API_KEY|LLM_PROVIDER"

echo ""
echo "Testing API..."
curl -s http://localhost:18500/api/health

echo ""
echo "=========================================="
echo "Update Complete!"
echo "=========================================="
echo ""
echo "Test query:"
echo '  curl -X POST http://localhost:18500/api/query -H "Content-Type: application/json" -d "{\"query\": \"What is ECU-750?\"}"'
echo ""
