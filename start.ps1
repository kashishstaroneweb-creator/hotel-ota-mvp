$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPython = Join-Path $RootDir "backend\.venv\Scripts\python.exe"
$FrontendNodeModules = Join-Path $RootDir "frontend\node_modules"

Write-Host "Starting OTA Revenue MVP..."
Write-Host ""

if (-not (Test-Path $BackendPython)) {
  Write-Host "Backend virtual environment not found."
  Write-Host "Run these first:"
  Write-Host "  cd backend"
  Write-Host "  python -m venv .venv"
  Write-Host "  .venv\Scripts\python -m pip install -r requirements.txt"
  exit 1
}

if (-not (Test-Path $FrontendNodeModules)) {
  Write-Host "Frontend dependencies not found."
  Write-Host "Run these first:"
  Write-Host "  cd frontend"
  Write-Host "  npm install"
  exit 1
}

Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host ""

$Backend = Start-Process `
  -FilePath $BackendPython `
  -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
  -WorkingDirectory (Join-Path $RootDir "backend") `
  -PassThru

try {
  Set-Location (Join-Path $RootDir "frontend")
  npm run dev
}
finally {
  if ($Backend -and -not $Backend.HasExited) {
    Stop-Process -Id $Backend.Id
  }
}

