@echo off
echo ========================================
echo Endurance Racing Tracker - Quick Start
echo ========================================
echo.

echo [1/4] Generating sample data...
python generate_sample_data.py
if errorlevel 1 (
    echo Error generating sample data!
    pause
    exit /b 1
)

echo.
echo [2/4] Starting FastAPI server...
echo.
echo Dashboard will be available at: http://localhost:8000/dashboard
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
