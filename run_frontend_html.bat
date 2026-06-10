@echo off
title TraderBlotter UI - HTML5 Terminal
color 0D
echo ===================================================
echo   LAUNCHING MODERN HTML5 FINTECH TERMINAL NODE     
echo ===================================================
echo [SYS] Resolving local directory paths...

:: Use the 'start' command to launch the file in the default system browser
start "" "%~dp0trader-dashboard\frontend\index.html"

echo [SYS] Browser tab opened successfully.
timeout /t 3 >nul