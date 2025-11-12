@echo off
echo ========================================
echo SuperEzio - Iniciar TODOS os Servidores
echo ========================================
echo.

REM Verificar se modelo existe
if not exist "models\qwen2.5-7b-instruct\config.json" (
    echo [ERRO] Modelo nao encontrado!
    echo Execute primeiro: python scripts\download_model.py
    pause
    exit /b 1
)

echo [1/3] Iniciando Backend Python (FastAPI)...
start "SuperEzio Python Backend" cmd /k "cd backend && venv\Scripts\activate && python api.py"

timeout /t 3 /nobreak >nul

echo [2/3] Iniciando Express Backend...
start "SuperEzio Express" cmd /k "npm run serve"

timeout /t 2 /nobreak >nul

echo [3/3] Iniciando Vite Frontend...
start "SuperEzio Vite" cmd /k "npm run dev"

echo.
echo ========================================
echo ✅ Todos os servidores iniciados!
echo ========================================
echo.
echo Python Backend: http://localhost:8000
echo Express Backend: http://localhost:8080
echo Vite Frontend:  http://localhost:3000
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul

