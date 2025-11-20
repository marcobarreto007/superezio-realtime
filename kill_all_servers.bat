@echo off
echo ========================================
echo SuperEzio - Encerrar TODOS os Servidores
echo ========================================
echo.

echo [1/3] Encerrando processos Python...
taskkill /F /IM python.exe /T >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Processos Python encerrados
) else (
    echo ℹ️  Nenhum processo Python encontrado
)

echo.
echo [2/3] Encerrando processos Node.js...
taskkill /F /IM node.exe /T >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Processos Node.js encerrados
) else (
    echo ℹ️  Nenhum processo Node.js encontrado
)

echo.
echo [3/3] Verificando portas...
timeout /t 2 /nobreak >nul

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Porta 8000 ainda em uso
) else (
    echo ✅ Porta 8000 livre
)

netstat -ano | findstr ":8080" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Porta 8080 ainda em uso
) else (
    echo ✅ Porta 8080 livre
)

netstat -ano | findstr ":3000" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Porta 3000 ainda em uso
) else (
    echo ✅ Porta 3000 livre
)

echo.
echo ========================================
echo ✅ Limpeza concluída!
echo ========================================
echo.
pause

