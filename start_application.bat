@echo off
echo Starting Backend...
start "Backend Server" /D "d:\steel\backend" run_server.bat

echo Starting Frontend...
start "Frontend Client" /D "d:\steel\frontend" run_frontend.bat

echo Opening Application...
timeout /t 5
start http://localhost:5173

echo Done! Both servers are running.
pause
