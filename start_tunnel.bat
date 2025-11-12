@echo off
echo =====================================
echo CLOUDFLARE TUNNEL - SuperEzio Backend
echo =====================================
echo.

REM Verificar se cloudflared está instalado
where cloudflared >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] cloudflared nao encontrado!
    echo.
    echo Instale com: winget install Cloudflare.cloudflared
    echo Ou baixe: https://github.com/cloudflare/cloudflared/releases
    pause
    exit /b 1
)

echo [OK] cloudflared encontrado
echo.

REM Verificar se config existe
if not exist cloudflared-config.yml (
    echo [ERRO] cloudflared-config.yml nao encontrado!
    echo.
    echo Crie o arquivo primeiro com:
    echo - tunnel ID correto
    echo - dominio correto
    pause
    exit /b 1
)

echo [OK] Config encontrado
echo.
echo Iniciando tunnel...
echo.
echo Backend local: http://localhost:8000
echo URL publica: Verifique no dashboard Cloudflare
echo.
echo Pressione Ctrl+C para parar o tunnel
echo.

cloudflared tunnel --config cloudflared-config.yml run

pause
