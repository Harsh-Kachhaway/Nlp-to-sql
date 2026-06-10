$Host.UI.RawUI.WindowTitle = "TraderBlotter UI - Gradio Node"
Clear-Host
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  INITIALIZING GRADIO 6 TERMINAL INTERFACE INTERCEPT  " -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Step into the parent directory, then into the project folder
Set-Location $PSScriptRoot
Set-Location .\trader-dashboard

Write-Host "[SYS] Generating portal access links..." -ForegroundColor Yellow
python "frontend/second frontend.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n[ERROR] Failed to compile or initialize the Gradio layout node." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}