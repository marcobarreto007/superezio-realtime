@echo off
cd /d "%~dp0backend"
echo Iniciando SuperEzio Backend...
venv\Scripts\python.exe api.py
pause
