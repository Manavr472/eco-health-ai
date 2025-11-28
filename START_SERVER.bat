@echo off
echo ========================================
echo   Eco-Health AI Platform - Startup
echo ========================================
echo.

cd /d "d:\Desktop\Mumbai_hacks\Agentic AI\eco-health-ai"

echo Starting API Server with Agent Integration...
echo.
echo Dashboard will be available at: http://localhost:8000
echo.

"d:\Desktop\Mumbai_hacks\Agentic AI\.conda\python.exe" -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload

pause
