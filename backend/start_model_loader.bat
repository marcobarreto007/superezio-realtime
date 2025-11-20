@echo off
REM Configurar encoding UTF-8 no terminal
chcp 65001 >nul 2>&1

echo ========================================
echo SuperEzio - Model Loader (Independente)
echo ========================================
echo.
echo Este processo carrega o modelo e mantem em memoria.
echo Outros componentes devem aguardar este processo iniciar.
echo.

REM Configurar encoding UTF-8 para Python
set PYTHONIOENCODING=utf-8

REM Verificar se modelo existe
if not exist "models\qwen2.5-7b-instruct\config.json" (
    echo [ERRO] Modelo nao encontrado!
    echo Execute primeiro: python scripts\download_model.py
    echo.
    pause
    exit /b 1
)

REM Navegar para backend
cd backend

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Iniciar model loader
echo [INFO] Iniciando Model Loader...
echo [INFO] Carregando modelo... (pode levar 1-2 minutos)
echo.
python model_loader.py

