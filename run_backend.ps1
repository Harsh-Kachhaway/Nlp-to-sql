$Host.UI.RawUI.WindowTitle = "TraderBlotter API Engine"
Clear-Host
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  INITIALIZING TRADERBLOTTER CORE FASTAPI BACKEND  " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

# Step into the parent directory, then into the project folder
Set-Location $PSScriptRoot
Set-Location .\trader-dashboard

Write-Host "[SYS] Launching asynchronous engine pipeline hooks..." -ForegroundColor Yellow
python -m app.main

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] The backend engine crashed or execution failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}