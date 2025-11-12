@echo off
echo ========================================
echo SuperEzio - Matar Processos nas Portas
echo ========================================
echo.

REM Matar porta 8000 (Python FastAPI)
echo [1/3] Verificando porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo   Matando processo %%a...
    taskkill /PID %%a /F >nul 2>&1
)

REM Matar porta 8080 (Express)
echo [2/3] Verificando porta 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo   Matando processo %%a...
    taskkill /PID %%a /F >nul 2>&1
)

REM Matar porta 3000 (Vite)
echo [3/3] Verificando porta 3000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    echo   Matando processo %%a...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo ✅ Processos encerrados!
echo.
timeout /t 2 /nobreak >nul

