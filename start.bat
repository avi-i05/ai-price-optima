@echo off
echo Starting AI PriceOptima Development Environment...
echo.

echo Starting FastAPI Backend...
start "Backend" cmd /k "cd backend && python main.py"

echo.
echo Starting React Frontend...
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both services are starting...
echo Backend: http://localhost:8001
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
