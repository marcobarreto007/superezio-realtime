@echo off
echo ========================================
echo SuperEzio Python Backend
echo ========================================
echo.

REM Configurar encoding UTF-8
set PYTHONIOENCODING=utf-8

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar se modelo existe
if not exist "..\models\qwen2.5-7b-instruct\config.json" (
    echo ERRO: Modelo nao encontrado!
    echo Execute primeiro: python ..\scripts\download_model.py
    pause
    exit /b 1
)

REM Iniciar servidor
echo Iniciando servidor FastAPI na porta 8000...
echo.
python api.py

pause

