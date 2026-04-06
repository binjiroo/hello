@echo off
setlocal EnableExtensions

cd /d "%~dp0"

echo [1/3] Checking port 5000...
set "FOUND_PID="
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":5000 .*LISTENING"') do (
    if not "%%P"=="0" (
        echo Stopping PID %%P on port 5000...
        taskkill /PID %%P /F >nul 2>&1
        set "FOUND_PID=1"
    )
)

if not defined FOUND_PID (
    echo No process is listening on port 5000.
)

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] venv\Scripts\python.exe was not found.
    exit /b 1
)

echo [2/3] Starting Flask development server...
echo     URL: http://127.0.0.1:5000/h_size/
echo [3/3] Press Ctrl+C to stop the server.

"venv\Scripts\python.exe" -m flask --app app:create_app run --debug --no-reload

endlocal
