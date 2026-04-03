# PowerShell Script - Update Qwen API Key and Restart Service

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Updating Qwen API Key Configuration" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Show current .env configuration
Write-Host "[1/4] Current .env configuration:" -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
Get-Content ..\.env | Select-String "LLM_PROVIDER|QWEN_API_KEY|OPENAI_API_KEY" | Select-Object -First 3

# Step 2: Rebuild MLflow model
Write-Host "`n[2/4] Rebuilding MLflow model with Qwen..." -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
cd ..
python scripts/log_mlflow_model.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: MLflow model rebuild failed!" -ForegroundColor Red
    exit 1
}

Write-Host "OK: MLflow model rebuilt successfully" -ForegroundColor Green

# Step 3: Restart Docker container
Write-Host "`n[3/4] Restarting Docker container..." -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
cd web
docker-compose down
docker-compose up -d

# Step 4: Wait and check status
Write-Host "`n[4/4] Waiting for service to start..." -ForegroundColor Yellow
Write-Host "--------------------------------" -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "`nChecking service status..." -ForegroundColor Cyan
docker-compose ps

Write-Host "`nChecking environment variables..." -ForegroundColor Cyan
docker-compose exec -T ecu-assistant-api printenv | Select-String "QWEN_API_KEY|LLM_PROVIDER"

Write-Host "`nTesting API..." -ForegroundColor Cyan
curl -s http://localhost:18500/api/health

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Update Complete!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Test query:" -ForegroundColor Yellow
Write-Host '  Invoke-RestMethod -Method Post -Uri "http://localhost:18500/api/query" -ContentType "application/json" -Body (@"{""query"": ""What is ECU-750?""}"@ | ConvertTo-Json)' -ForegroundColor White
Write-Host ""
