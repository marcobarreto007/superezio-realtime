@echo off
REM Configurar encoding UTF-8 no terminal
chcp 65001 >nul 2>&1

echo ========================================
echo SuperEzio - Iniciar TODOS (ORDEM CORRETA)
echo ========================================
echo.
echo ORDEM DE INICIALIZACAO:
echo   1. Limpar processos duplicados
echo   2. Python FastAPI (carrega modelo e serve API)
echo   3. Express Backend
echo   4. Vite Frontend
echo.
echo OTIMIZACAO: Model Loader removido (economiza ~4-5 GB VRAM)
echo.

REM Limpar processos duplicados primeiro
echo [0/4] Limpando processos duplicados...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Processos limpos
echo.

REM Verificar se modelo existe
if not exist "models\qwen2.5-7b-instruct\config.json" (
    echo [ERRO] Modelo nao encontrado!
    echo Execute primeiro: python scripts\download_model.py
    pause
    exit /b 1
)

echo [1/4] Iniciando Python FastAPI (carregando modelo + servindo API)...
echo NOTA: Carregamento do modelo leva ~90-120 segundos na primeira vez
start "SuperEzio Python Backend" cmd /k "cd backend && set PYTHONIOENCODING=utf-8 && set PYTHONUTF8=1 && venv\Scripts\activate && python api.py"

echo.
echo Aguardando Python FastAPI inicializar (10 segundos)...
timeout /t 10 /nobreak >nul

echo.
echo [2/4] Iniciando Express Backend...
start "SuperEzio Express" cmd /k "npm run serve"

timeout /t 2 /nobreak >nul

echo.
echo [3/4] Iniciando Vite Frontend...
start "SuperEzio Vite" cmd /k "npm run dev"

echo.
echo ========================================
echo ✅ Todos os servidores iniciados!
echo ========================================
echo.
echo Python Backend: http://localhost:8000 (modelo carregado aqui)
echo Express Backend: http://localhost:8080
echo Vite Frontend:  http://localhost:3000
echo.
echo OTIMIZACAO APLICADA:
echo - Model Loader separado removido
echo - Economia de VRAM: ~4-5 GB (50%%)
echo - O modelo e carregado diretamente pelo FastAPI
echo.
pause

