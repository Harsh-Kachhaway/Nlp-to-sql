@echo off
title TraderBlotter UI - Gradio Node
color 0A
echo ===================================================
echo   INITIALIZING GRADIO 6 TERMINAL INTERFACE INTERCEPT  
echo ===================================================
echo [SYS] Entering project code directory...
cd /d "%~dp0"
cd trader-dashboard
echo [SYS] Generating portal access links...
python "frontend/frontend_app.py"
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Failed to compile or initialize the Gradio layout node.
    pause
)