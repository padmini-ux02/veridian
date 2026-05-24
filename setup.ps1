# Veridian — Quick Start Script
# Run this from the project root directory

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Veridian - Setup & Launch" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Install frontend dependencies
Write-Host "`n[1/3] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: npm install failed" -ForegroundColor Red; exit 1 }
Write-Host "Frontend dependencies installed!" -ForegroundColor Green
Set-Location ..

# Install backend dependencies (in venv)
Write-Host "`n[2/3] Setting up Python virtual environment..." -ForegroundColor Yellow
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: pip install failed" -ForegroundColor Red; exit 1 }
Write-Host "Backend dependencies installed!" -ForegroundColor Green
Set-Location ..

Write-Host "`n[3/3] Setup Complete!" -ForegroundColor Green
Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host " To start the application:" -ForegroundColor White
Write-Host " Option A (Docker - Recommended):" -ForegroundColor Yellow
Write-Host "   docker-compose up --build" -ForegroundColor White
Write-Host "`n Option B (Local Development):" -ForegroundColor Yellow
Write-Host "   Terminal 1 (Backend):" -ForegroundColor White
Write-Host "     cd backend && venv\Scripts\activate && uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "   Terminal 2 (Frontend):" -ForegroundColor White
Write-Host "     cd frontend && npm run dev" -ForegroundColor Gray
Write-Host "`n Default Admin Credentials:" -ForegroundColor Yellow
Write-Host "   Email:    admin@veridian.io" -ForegroundColor White
Write-Host "   Password: Admin@123456" -ForegroundColor White
Write-Host "`n Endpoints:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================`n" -ForegroundColor Cyan
