@echo off
rem Запуск веб-интерфейса проекта «Экскурсионное бюро».
rem Использует интерпретатор из виртуального окружения .venv.
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" goto no_venv

echo Запускаю сервер разработки Django...
echo Откройте в браузере: http://127.0.0.1:8000/
echo Остановить сервер: Ctrl+C
echo.

".venv\Scripts\python.exe" manage.py runserver
pause
exit /b 0

:no_venv
echo Виртуальное окружение .venv не найдено.
echo Создайте его и установите зависимости:
echo.
echo   py -3.12 -m venv .venv
echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
echo   .venv\Scripts\python.exe manage.py migrate
echo   .venv\Scripts\python.exe -m db.import_json
echo.
pause
exit /b 1
