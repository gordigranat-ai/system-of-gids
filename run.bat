@echo off
rem Launch script for the guide service console application.
rem If the virtual environment .venv exists, its interpreter is used.
chcp 65001 > nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)

pause
