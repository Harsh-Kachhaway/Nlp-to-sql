@echo off
title TraderBlotter API Engine
color 0B
echo ===================================================
echo   INITIALIZING TRADERBLOTTER CORE FASTAPI BACKEND  
echo ===================================================
echo [SYS] Entering project code directory...
cd /d "%~dp0"
cd trader-dashboard
echo [SYS] Launching asynchronous engine pipeline hooks...
python -m app.main
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] The backend engine crashed or execution failed.
    pause
)