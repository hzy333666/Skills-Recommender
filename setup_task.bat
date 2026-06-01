@echo off
REM ============================================================
REM Create Windows Scheduled Task
REM Run this script as Administrator
REM ============================================================

echo Creating Windows Scheduled Task...
echo.

schtasks /create /tn "Skills-Recommender-Daily" /tr "G:\Skills-Recommender\run_daily.bat" /sc daily /st 08:00 /f

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS! Task created:
    echo   Name: Skills-Recommender-Daily
    echo   Schedule: Daily at 08:00
    echo   Script: G:\Skills-Recommender\run_daily.bat
    echo.
    echo You can view/edit this task in Task Scheduler (taskschd.msc)
) else (
    echo.
    echo FAILED! Please run this script as Administrator.
)

pause
