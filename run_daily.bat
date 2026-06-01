@echo off
REM ============================================================
REM Skills-Recommender Daily Run Script
REM
REM Usage:
REM   Manual: run_daily.bat
REM   Scheduled: Use Windows Task Scheduler to run this script
REM ============================================================

cd /d "%~dp0"

echo [%date% %time%] Starting run >> logs\daily.log

python main.py >> logs\daily.log 2>&1

if %errorlevel% neq 0 (
    echo [%date% %time%] FAILED with code: %errorlevel% >> logs\daily.log
    exit /b %errorlevel%
)

echo [%date% %time%] Completed >> logs\daily.log
