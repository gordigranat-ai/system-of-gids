@echo off
rem Guide service: start the Django development server and open it in a browser.
setlocal
rem Clear the debug flag so the CSS is always served.
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

echo Starting the Django development server in a separate window...
start "guide_service - Django server" cmd /k ".venv\Scripts\python.exe manage.py runserver"

echo Waiting for the server...
timeout /t 5 /nobreak >nul

echo Opening http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"

echo.
echo If the page did not open, look at the server window for an error.
echo Press Ctrl+C in the server window to stop the server.
timeout /t 8 /nobreak >nul
exit /b 0
