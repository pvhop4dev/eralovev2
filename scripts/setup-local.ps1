# Eralove — Local Development Setup Script (Windows PowerShell)
# Usage: .\scripts\setup-local.ps1

Write-Host ""
Write-Host "💗 Eralove — Setting up local development environment..." -ForegroundColor Magenta
Write-Host ""

# ── 1. Check Docker ──────────────────────────────────────
Write-Host "🐳 Checking Docker..." -ForegroundColor Cyan
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "  ✅ Docker is running" -ForegroundColor Green

# ── 2. Start Infrastructure ──────────────────────────────
Write-Host ""
Write-Host "🏗️  Starting infrastructure services..." -ForegroundColor Cyan
docker compose -f infra/docker-compose.yml up -d
Write-Host "  ✅ PostgreSQL, Redis, MinIO, Mailpit started" -ForegroundColor Green

# ── 3. Copy .env ─────────────────────────────────────────
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "  ✅ Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  .env already exists, skipping" -ForegroundColor Yellow
}

# ── 4. Python Virtual Environment ────────────────────────
Write-Host ""
Write-Host "🐍 Setting up Python environment..." -ForegroundColor Cyan
if (-not (Test-Path "apps/api/.venv")) {
    python -m venv apps/api/.venv
    Write-Host "  ✅ Created virtual environment" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  Virtual environment exists, skipping" -ForegroundColor Yellow
}

& apps/api/.venv/Scripts/pip.exe install -r apps/api/requirements-dev.txt --quiet
Write-Host "  ✅ Python dependencies installed" -ForegroundColor Green

# ── 5. Node Dependencies ────────────────────────────────
Write-Host ""
Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Cyan
npm install
Write-Host "  ✅ Node dependencies installed" -ForegroundColor Green

# ── 6. Database Migration ────────────────────────────────
Write-Host ""
Write-Host "🗄️  Running database migrations..." -ForegroundColor Cyan
Push-Location apps/api
& .venv/Scripts/python.exe -m alembic upgrade head
Pop-Location
Write-Host "  ✅ Database migrations applied" -ForegroundColor Green

# ── 7. Summary ───────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  💗 Eralove dev environment is ready!" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host ""
Write-Host "  🌐 Frontend:  http://localhost:3000" -ForegroundColor White
Write-Host "  🚀 Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "  📖 API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host "  📧 Mailpit:   http://localhost:8025" -ForegroundColor White
Write-Host "  📦 MinIO:     http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "  Start developing:" -ForegroundColor Yellow
Write-Host "    npm run dev          # Start both frontend & backend" -ForegroundColor Gray
Write-Host "    npm run dev:web      # Start frontend only" -ForegroundColor Gray
Write-Host ""
