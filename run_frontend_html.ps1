$Host.UI.RawUI.WindowTitle = "TraderBlotter UI - HTML5 Terminal"
Clear-Host
Write-Host "===================================================" -ForegroundColor Magenta
Write-Host "  LAUNCHING MODERN HTML5 FINTECH TERMINAL NODE     " -ForegroundColor Magenta
Write-Host "===================================================" -ForegroundColor Magenta

# Resolve path and launch using the default system handler
$HtmlPath = Join-Path $PSScriptRoot "trader-dashboard\frontend\index.html"
Write-Host "[SYS] Opening terminal view at: $HtmlPath" -ForegroundColor Yellow

Start-Process $HtmlPath

Write-Host "[SYS] Browser tab opened successfully." -ForegroundColor Green
Start-Sleep -Seconds 3