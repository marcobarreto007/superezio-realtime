@echo off
echo ========================================
echo SuperEzio - Status dos Servidores
echo ========================================
echo.

echo [1/3] Python FastAPI (porta 8000):
netstat -ano | findstr :8000 >nul
if %errorlevel% == 0 (
    echo   ✅ RODANDO
) else (
    echo   ❌ PARADO
)

echo.
echo [2/3] Express Backend (porta 8080):
netstat -ano | findstr :8080 >nul
if %errorlevel% == 0 (
    echo   ✅ RODANDO
) else (
    echo   ❌ PARADO
)

echo.
echo [3/3] Vite Frontend (porta 3000):
netstat -ano | findstr :3000 >nul
if %errorlevel% == 0 (
    echo   ✅ RODANDO
) else (
    echo   ❌ PARADO
)

echo.
echo ========================================
pause

