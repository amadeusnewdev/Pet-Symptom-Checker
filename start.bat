@echo off
REM SNOUTIQ Backend Startup Script for Windows

echo Starting SNOUTIQ Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run: python -m venv venv
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found!
    echo Please copy .env.example to .env and add your API key
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if datasets exist
dir /b datasets\master_*_dataset.json >nul 2>&1
if errorlevel 1 (
    echo Warning: No dataset files found in datasets/
    echo Please add your JSON dataset files to backend\datasets\
    exit /b 1
)

echo Starting Flask API...
python app.py
