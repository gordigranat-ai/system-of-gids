@echo off
rem Guide service: start the Django development server and open it in a browser.
setlocal
rem Drop the debug flag so the CSS is always served.
set "DJANGO_DEBUG="
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment .venv was not found.
    echo Create it and install dependencies:
    echo     py -3.12 -m venv .venv
    echo     .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo     .venv\Scripts\python.exe manage.py migrate
    echo     .venv\Scripts\python.exe -m db.import_json
    echo.
    pause
    exit /b 1
)

rem If the port is already busy, the server is running: just open the browser.
powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue) { exit 0 } else { exit 1 }"
if not errorlevel 1 (
    echo The server is already running on port 8000.
    start "" "http://127.0.0.1:8000/"
    timeout /t 3 /nobreak >nul
    exit /b 0
)

echo Starting the Django development server in a separate window...
start "guide_service - Django server" cmd /k ".venv\Scripts\python.exe manage.py runserver"

echo Waiting for the server...
timeout /t 5 /nobreak >nul

echo Opening http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

echo.
echo If the page looks wrong, press Ctrl+F5 in the browser to reload the styles.
echo To stop the server press Ctrl+C in the server window.
timeout /t 8 /nobreak >nul
exit /b 0
