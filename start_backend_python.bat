@echo off
REM Configurar encoding UTF-8 no terminal
chcp 65001 >nul 2>&1

echo ========================================
echo SuperEzio - Iniciar Backend Python
echo ========================================
echo.

REM Define o cache do Hugging Face para um diretorio local
set HF_HOME=%~dp0.cache\huggingface
echo [INFO] Cache do Hugging Face definido para: %HF_HOME%

REM Configurar encoding UTF-8 para Python
set PYTHONIOENCODING=utf-8

REM Verificar se modelo existe
if not exist "models\qwen2.5-7b-instruct\config.json" (
    echo [ERRO] Modelo nao encontrado!
    echo.
    echo Execute primeiro:
    echo   python scripts\download_model.py
    echo.
    pause
    exit /b 1
)

REM Navegar para backend
cd backend

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Iniciar servidor
echo [INFO] Iniciando servidor FastAPI na porta 8000...
echo [INFO] Carregando modelo... (pode levar 1-2 minutos)
echo.
python api.py

