# START BACKEND
# Run this in Terminal 1

Write-Host "Starting Backend Server..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn backend.main:app --reload
