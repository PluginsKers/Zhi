@echo off
echo Starting ZHI AI System...
echo.

echo Starting Python WebSocket Proxy Server...
start "WebSocket Proxy" python server.py

echo Waiting for proxy server to start...
timeout /t 3 /nobreak > nul

echo Starting Vue Development Server...
start "Vue Dev Server" npm run dev

echo.
echo ZHI AI System is starting...
echo Frontend: http://localhost:5173
echo WebSocket Proxy: ws://localhost:8765
echo.
echo Press any key to stop all services...
pause > nul

echo Stopping services...
taskkill /f /im python.exe > nul 2>&1
taskkill /f /im node.exe > nul 2>&1
echo Services stopped. 