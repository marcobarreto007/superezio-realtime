@echo off
echo ================================================
echo SUPEREZIO - Backend + Cloudflare Tunnel
echo ================================================
echo.

REM Iniciar Backend Python em background
echo [1/2] Iniciando Backend Python (FastAPI)...
start "SuperEzio Backend" /MIN cmd /c "cd backend && python api.py"
timeout /t 3 /nobreak >nul
echo [OK] Backend rodando em http://localhost:8000
echo.

REM Iniciar Cloudflare Tunnel
echo [2/2] Iniciando Cloudflare Tunnel...
echo [INFO] Backend vai ficar acessivel via teu dominio
echo.
start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --config cloudflared-config.yml run"

echo.
echo ================================================
echo SUPEREZIO ONLINE!
echo ================================================
echo Backend Local:  http://localhost:8000
echo Backend Publico: https://api.teudominio.com
echo.
echo Para parar: feche as janelas do Backend e Tunnel
echo ================================================
pause
