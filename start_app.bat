@echo off
echo ===================================================
echo   Steel Application Startup Script
echo ===================================================

echo [1/2] Starting Backend Server (New Window)...
start "Steel Backend" cmd /k "cd /d D:\steel\backend && call run_server.bat"

echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/2] Starting Frontend Server (New Window)...
start "Steel Frontend" cmd /k "cd /d D:\steel\frontend && npm run dev"

echo ===================================================
echo   All systems launched!
echo   - Backend: http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo   - MongoDB: http://localhost:27017
echo ===================================================
echo You can minimize the popup windows, but DO NOT CLOSE THEM.
pause
